#!/usr/bin/env python3
"""OpenStreetMap 행정경계로 여행 지역 선택 화면의 시도·시군구 윤곽 GeoJSON 을 만든다.

데이터 출처: © OpenStreetMap contributors. 원 데이터와 이 스크립트의 결과 파일은
Open Database License(ODbL) 1.0 을 따른다(assets/geo/LICENSE-ODbL.md).

하는 일
  1. Overpass API 에서 대한민국 안의 boundary=administrative 관계를 받는다.
     admin_level 4(광역)와 6(시·군·구).
  2. 관계의 바깥·안쪽 길을 이어 다각형으로 만든다.
  3. 앱의 지역 목록(lib/common/constants/korea_regions.dart)에 맞춰 시군구를
     고른다. 앱은 서버가 받는 표기(옛 시도 이름 포함)를 쓰므로 이름은 앱 목록을 따른다.
  4. 한국 OSM 의 해안 쪽 경계는 영해까지 포함하므로, OSM 해안선에서 만든 육지
     다각형(osmdata.openstreetmap.de 의 simplified land polygons, ODbL)으로 잘라
     바다 부분을 덜어 낸다.
  5. 시군구 경계를 위상을 지키며 단순화하고, 시도 윤곽은 그 시군구들을 합쳐 만든다.
     그래서 시도와 시군구의 경계선이 서로 어긋나지 않는다.
  6. 파일마다 크기 상한(기본 900KB)을 넘지 않도록 허용 오차를 키워 가며 쓴다.

앱 목록과 OSM 이 어긋나는 지역(행정구역 개편 등)은 표준 오류로 보고한다.
--strict 를 주면 그런 지역이 하나라도 있을 때 실패한다.

쓰임
    python3 -m pip install shapely pyshp
    python3 scripts/build_geo.py [--cache DIR] [--strict]
"""
import argparse
import io
import json
import math
from pathlib import Path
import re
import sys
import time
import urllib.parse
import urllib.request
import zipfile

import shapefile
from shapely import coverage_simplify, make_valid
from shapely.geometry import LineString, MultiPolygon, Polygon, mapping, shape
from shapely.ops import linemerge, polygonize, unary_union

ROOT = Path(__file__).resolve().parents[1]
REGIONS = ROOT / 'lib/common/constants/korea_regions.dart'
OUT = ROOT / 'assets/geo'
ENDPOINTS = (
    'https://overpass-api.de/api/interpreter',
    'https://overpass.private.coffee/api/interpreter',
    'https://maps.mail.ru/osm/tools/overpass/api/interpreter',
)
QUERY = ('[out:json][timeout:900];area["ISO3166-1"="KR"]["admin_level"="2"]->.kr;'
         'relation["boundary"="administrative"]["admin_level"="{level}"](area.kr);out geom;')
USER_AGENT = 'map-project-client build_geo.py'
LAND_URL = 'https://osmdata.openstreetmap.de/download/simplified-land-polygons-complete-3857.zip'
# 대한민국을 덮는 경위도 범위(서, 남, 동, 북). 육지 다각형은 이 안의 것만 쓴다.
KOREA_BBOX = (124.0, 32.8, 132.2, 39.0)
EARTH_RADIUS = 6378137.0
ATTRIBUTION = {
    'attribution': '© OpenStreetMap contributors',
    'license': 'ODbL-1.0',
    'source': 'https://www.openstreetmap.org/copyright',
}

# 행정안전부 행정기관코드 앞 두 자리 → 앱 목록의 시도 이름. OSM 시군구 관계의
# ref:KR:mois:admin 으로 시도를 정한다. 앱은 서버 표기(개칭 전 이름)를 쓴다.
CODE_TO_PROVINCE = {
    '11': '서울특별시', '26': '부산광역시', '27': '대구광역시', '28': '인천광역시',
    '29': '광주광역시', '30': '대전광역시', '31': '울산광역시', '36': '세종특별자치시',
    '41': '경기도', '42': '강원도', '43': '충청북도', '44': '충청남도', '45': '전라북도',
    '46': '전라남도', '47': '경상북도', '48': '경상남도', '50': '제주특별자치도',
    '51': '강원도', '52': '전라북도',
}
# 코드가 없는 시군구는 이 광역 윤곽 안에 있는지로 시도를 정한다(OSM 이름 → 앱 이름).
LEVEL4_ALIASES = {'강원특별자치도': '강원도', '전북특별자치도': '전라북도'}
# 앱 목록 이름이 OSM 에 그대로 없을 때 합쳐 쓸 OSM 시군구(개편으로 나뉜 곳).
DISTRICT_ALIASES = {
    ('인천광역시', '서구'): ('서해구', '검단구'),
}
# 단층제라 시군구 관계가 없는 곳은 광역 윤곽을 그대로 쓴다.
SINGLE_TIER = {'세종특별자치시'}


def read_regions():
    text = REGIONS.read_text(encoding='utf-8')
    provinces = re.findall(r"'([^']+)'", re.search(
        r'kProvinces\s*=\s*\[(.*?)\];', text, re.S).group(1))
    body = re.search(r'kCitiesByProvince\s*=\s*\{(.*?)\n\};', text, re.S).group(1)
    cities = {p: re.findall(r"'([^']+)'", b)
              for p, b in re.findall(r"'([^']+)':\s*\[(.*?)\]", body, re.S)}
    if sorted(cities) != sorted(provinces):
        sys.exit('build_geo: kProvinces and kCitiesByProvince disagree')
    return provinces, cities


def overpass(level, cache):
    path = cache / f'osm-admin-level-{level}.json' if cache else None
    if path and path.exists():
        return json.loads(path.read_text(encoding='utf-8'))
    data = urllib.parse.urlencode({'data': QUERY.format(level=level)}).encode()
    for attempt in range(6):
        url = ENDPOINTS[attempt % len(ENDPOINTS)]
        request = urllib.request.Request(url, data=data, headers={'User-Agent': USER_AGENT})
        try:
            with urllib.request.urlopen(request, timeout=900) as response:
                raw = response.read()
            parsed = json.loads(raw)
        except (OSError, ValueError) as error:
            wait = 15 * 2 ** attempt
            print(f'build_geo: {url} level {level}: {error}; retry in {wait}s', file=sys.stderr)
            time.sleep(wait)
            continue
        if path:
            path.write_bytes(raw)
        return parsed
    sys.exit(f'build_geo: could not download admin_level {level}')


def download(url, path):
    if path and path.exists():
        return path.read_bytes()
    for attempt in range(4):
        request = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
        try:
            with urllib.request.urlopen(request, timeout=600) as response:
                raw = response.read()
        except OSError as error:
            wait = 15 * 2 ** attempt
            print(f'build_geo: {url}: {error}; retry in {wait}s', file=sys.stderr)
            time.sleep(wait)
            continue
        if path:
            path.write_bytes(raw)
        return raw
    sys.exit(f'build_geo: could not download {url}')


def to_lonlat(x, y):
    """웹 메르카토르(EPSG:3857) 좌표를 경위도로 바꾼다."""
    return (math.degrees(x / EARTH_RADIUS),
            math.degrees(2 * math.atan(math.exp(y / EARTH_RADIUS)) - math.pi / 2))


def land_polygons(cache):
    """OSM 해안선에서 만든 육지 다각형 중 한국 범위에 걸치는 것을 합친다."""
    raw = download(LAND_URL, cache / 'simplified-land-polygons-complete-3857.zip' if cache else None)
    archive = zipfile.ZipFile(io.BytesIO(raw))
    names = {Path(n).suffix: n for n in archive.namelist() if Path(n).stem.endswith('land_polygons')}
    reader = shapefile.Reader(shp=io.BytesIO(archive.read(names['.shp'])),
                              shx=io.BytesIO(archive.read(names['.shx'])),
                              dbf=io.BytesIO(archive.read(names['.dbf'])))
    west, south = (EARTH_RADIUS * math.radians(KOREA_BBOX[0]),
                   EARTH_RADIUS * math.log(math.tan(math.pi / 4 + math.radians(KOREA_BBOX[1]) / 2)))
    east, north = (EARTH_RADIUS * math.radians(KOREA_BBOX[2]),
                   EARTH_RADIUS * math.log(math.tan(math.pi / 4 + math.radians(KOREA_BBOX[3]) / 2)))
    polygons = []
    for item in reader.iterShapes():
        x0, y0, x1, y1 = item.bbox
        if x1 < west or x0 > east or y1 < south or y0 > north:
            continue
        geometry = shape(item.__geo_interface__)
        rings = []
        for polygon in polygons_of(geometry):
            exterior = [to_lonlat(x, y) for x, y in polygon.exterior.coords]
            holes = [[to_lonlat(x, y) for x, y in ring.coords] for ring in polygon.interiors]
            rings.append(Polygon(exterior, holes))
        polygons.extend(rings)
    return make_valid(unary_union(polygons))


def relation_geometry(relation):
    outer, inner = [], []
    for member in relation.get('members', []):
        if member.get('type') != 'way' or len(member.get('geometry') or []) < 2:
            continue
        line = LineString([(p['lon'], p['lat']) for p in member['geometry']])
        (inner if member.get('role') == 'inner' else outer).append(line)
    if not outer:
        return None
    shell = unary_union(list(polygonize(linemerge(outer))))
    if inner:
        shell = shell.difference(unary_union(list(polygonize(linemerge(inner)))))
    shell = make_valid(shell)
    polygons = [g for g in getattr(shell, 'geoms', [shell]) if isinstance(g, Polygon)]
    return unary_union(polygons) if polygons else None


def load(level, cache):
    features = []
    for element in overpass(level, cache).get('elements', []):
        if element.get('type') != 'relation':
            continue
        geometry = relation_geometry(element)
        if geometry is not None and not geometry.is_empty:
            features.append((element.get('tags', {}), geometry))
    return features


def assign_province(tags, geometry, level4, cities):
    code = tags.get('ref:KR:mois:admin', '')[:2]
    if code in CODE_TO_PROVINCE:
        return CODE_TO_PROVINCE[code]
    point = geometry.representative_point()
    for name, area in level4:
        if area.contains(point):
            name = LEVEL4_ALIASES.get(name, name)
            if name in cities:
                return name
            # 통합된 광역(예: 여러 시도가 합쳐진 경우)은 앱 목록에서 이름을 가진 쪽으로.
            owners = [p for p, names in cities.items() if tags.get('name') in names]
            return owners[0] if len(owners) == 1 else None
    return None


def polygons_of(geometry):
    if isinstance(geometry, Polygon):
        return [geometry] if not geometry.is_empty else []
    return [p for g in getattr(geometry, 'geoms', []) for p in polygons_of(g)]


def drop_specks(geometry, min_area):
    """작은 섬 조각을 뺀다. 조각마다 지도 오버레이가 하나씩 생기기 때문이다."""
    parts = polygons_of(geometry)
    if not parts:
        return Polygon()
    keep = [p for p in parts if p.area >= min_area] or [max(parts, key=lambda p: p.area)]
    return keep[0] if len(keep) == 1 else MultiPolygon(keep)


def rounded(geometry):
    def ring(coords):
        return [[round(x, 5), round(y, 5)] for x, y in coords]
    shapes = []
    for polygon in getattr(geometry, 'geoms', [geometry]):
        rings = [ring(polygon.exterior.coords)] + [ring(r.coords) for r in polygon.interiors]
        if len(rings[0]) >= 4:
            shapes.append(rings)
    if len(shapes) == 1:
        return {'type': 'Polygon', 'coordinates': shapes[0]}
    return {'type': 'MultiPolygon', 'coordinates': shapes}


def collection(features):
    return json.dumps({'type': 'FeatureCollection', **ATTRIBUTION, 'features': features},
                      ensure_ascii=False, separators=(',', ':'))


def build(provinces, cities, districts, english, tolerance, min_area):
    order = [(p, c) for p in provinces for c in cities[p] if (p, c) in districts]
    geoms = [districts[key] for key in order]
    try:
        simplified = list(coverage_simplify(geoms, tolerance))
    except Exception:  # 겹치는 윤곽이 있으면 위상 단순화가 안 된다 — 하나씩 줄인다.
        simplified = [g.simplify(tolerance, preserve_topology=True) for g in geoms]
    simplified = [drop_specks(make_valid(g), min_area) for g in simplified]
    district_features, by_province = [], {p: [] for p in provinces}
    for (province, city), geometry in zip(order, simplified):
        p_index = provinces.index(province) + 1
        c_index = cities[province].index(city) + 1
        district_features.append({'type': 'Feature', 'properties': {
            'SIG_CD': f'{p_index:02d}{c_index:03d}', 'SIG_KOR_NM': city,
            'SIG_ENG_NM': english.get((province, city), '')},
            'geometry': rounded(geometry)})
        by_province[province].append(geometry)
    province_features = []
    for index, province in enumerate(provinces, 1):
        if not by_province[province]:
            continue
        merged = drop_specks(make_valid(unary_union(by_province[province])), min_area)
        province_features.append({'type': 'Feature', 'properties': {
            'CTPRVN_CD': f'{index:02d}', 'CTP_KOR_NM': province,
            'CTP_ENG_NM': english.get((province, None), '')},
            'geometry': rounded(merged)})
    return collection(province_features), collection(district_features)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    parser.add_argument('--cache', type=Path, help='Overpass 응답을 저장·재사용할 폴더')
    parser.add_argument('--strict', action='store_true', help='앱 목록과 어긋나면 실패')
    parser.add_argument('--max-bytes', type=int, default=900_000)
    args = parser.parse_args(argv)
    if args.cache:
        args.cache.mkdir(parents=True, exist_ok=True)

    provinces, cities = read_regions()
    level4_features = load(4, args.cache)
    level4 = [(t.get('name', ''), g) for t, g in level4_features]
    level6 = load(6, args.cache)

    english = {}
    for tags, geometry in level4_features:
        name = LEVEL4_ALIASES.get(tags.get('name', ''), tags.get('name', ''))
        if name in cities:
            english[(name, None)] = tags.get('name:en', '')
            if name in SINGLE_TIER:
                english[(name, name)] = tags.get('name:en', '')

    found = {}
    for tags, geometry in level6:
        province = assign_province(tags, geometry, level4, cities)
        if province:
            found.setdefault((province, tags.get('name', '')), []).append((tags, geometry))

    districts, missing = {}, []
    for province in provinces:
        for city in cities[province]:
            parts = found.get((province, city))
            if not parts and (province, city) in DISTRICT_ALIASES:
                parts = [x for alias in DISTRICT_ALIASES[(province, city)]
                         for x in found.get((province, alias), [])]
            if not parts and province in SINGLE_TIER and city == province:
                parts = [({'name:en': english.get((province, None), '')}, g)
                         for n, g in level4 if LEVEL4_ALIASES.get(n, n) == province]
            if not parts:
                missing.append(f'{province} {city}')
                continue
            districts[(province, city)] = unary_union([g for _, g in parts])
            english.setdefault((province, city), parts[0][0].get('name:en', ''))
    wanted = {(p, c) for p in provinces for c in cities[p]}
    used_aliases = {(p, a) for (p, _), names in DISTRICT_ALIASES.items() for a in names}
    extra = sorted(f'{p} {c}' for p, c in found if (p, c) not in wanted and (p, c) not in used_aliases)
    if missing:
        print('build_geo: no OSM outline for: ' + ', '.join(missing), file=sys.stderr)
    if extra:
        print('build_geo: OSM districts not in the app list (left out): ' + ', '.join(extra), file=sys.stderr)
    if args.strict and missing:
        return 1
    # 윤곽이 없는 지역은 파일에 넣지 않는다. 앱은 그 지역을 지도 오버레이 없이 목록으로만 고른다.

    land = land_polygons(args.cache)
    for key, geometry in list(districts.items()):
        clipped = make_valid(geometry.intersection(land))
        if polygons_of(clipped):
            districts[key] = unary_union(polygons_of(clipped))

    # 약 10km² 보다 작은 섬 조각은 뺀다(조각마다 지도 오버레이가 하나씩 생긴다).
    # 시군구마다 가장 큰 조각은 크기와 상관없이 남긴다.
    tolerance, min_area = 0.0005, 0.001
    for _ in range(12):
        province_json, district_json = build(provinces, cities, districts, english,
                                             tolerance, min_area)
        sizes = (len(province_json.encode()), len(district_json.encode()))
        if max(sizes) <= args.max_bytes:
            break
        tolerance *= 1.4
    else:
        sys.exit('build_geo: could not fit the size limit')
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'provinces.geojson').write_text(province_json + '\n', encoding='utf-8')
    (OUT / 'districts.geojson').write_text(district_json + '\n', encoding='utf-8')
    print(f'build_geo: tolerance {tolerance:.5f}°, provinces {sizes[0]} B, districts {sizes[1]} B, '
          f'{len(wanted) - len(missing)}/{len(wanted)} districts with outlines', file=sys.stderr)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
