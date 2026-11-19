import 'dart:convert';
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:map_project_client/common/constants/korea_regions.dart';

/// 지역 선택 지도가 읽는 시도·시군구 윤곽 자료와 앱 지역 목록의 약속.
///
/// 화면은 시도 이름으로 시도 코드를 찾고, 시군구 코드가 그 시도 코드로 시작하는지로
/// 윤곽을 고른다(trip_step5_screen.dart). 이 약속이 깨지면 지도에 윤곽이 뜨지 않는다.
Map<String, dynamic> _load(String path) =>
    jsonDecode(File(path).readAsStringSync()) as Map<String, dynamic>;

void main() {
  final provinces = _load('assets/geo/provinces.geojson');
  final districts = _load('assets/geo/districts.geojson');

  test('both files carry the OpenStreetMap attribution and stay under 1MB', () {
    for (final path in [
      'assets/geo/provinces.geojson',
      'assets/geo/districts.geojson',
    ]) {
      expect(File(path).lengthSync(), lessThan(1000000), reason: path);
      final data = _load(path);
      expect(data['attribution'], '© OpenStreetMap contributors');
      expect(data['license'], 'ODbL-1.0');
    }
  });

  test('every province in the app list has exactly one outline', () {
    final names = [
      for (final f in provinces['features'] as List)
        (f['properties'] as Map)['CTP_KOR_NM'] as String,
    ];
    expect(names.toSet(), kProvinces.toSet());
    expect(names.length, kProvinces.length);
  });

  test('district codes start with their province code and use app names', () {
    final codeOf = {
      for (final f in provinces['features'] as List)
        (f['properties'] as Map)['CTP_KOR_NM'] as String:
            (f['properties'] as Map)['CTPRVN_CD'] as String,
    };
    final outlined = <String>{};
    for (final f in districts['features'] as List) {
      final props = f['properties'] as Map;
      final code = props['SIG_CD'] as String;
      final name = props['SIG_KOR_NM'] as String;
      final province = codeOf.entries
          .firstWhere((e) => code.startsWith(e.value))
          .key;
      expect(kCitiesByProvince[province], contains(name), reason: code);
      outlined.add('$province $name');
      expect((f['geometry'] as Map)['type'], anyOf('Polygon', 'MultiPolygon'));
    }
    // OSM 이 이미 개편된 구역으로 바뀐 곳은 윤곽 없이 목록으로만 고른다(docs/data.md).
    final missing = [
      for (final p in kProvinces)
        for (final c in kCitiesByProvince[p]!)
          if (!outlined.contains('$p $c')) '$p $c',
    ];
    expect(missing, ['인천광역시 중구', '인천광역시 동구']);
  });
}
