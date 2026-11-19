# 데이터 카드

앱 저장소에 담았거나 빌드 때 받는 자료와, 앱이 실행 중에 서버를 거쳐 보여 주기만 하는 자료를 나눠 적는다.

## 저장소에 담은 자료

### 행정경계 윤곽 — `assets/geo/provinces.geojson`, `assets/geo/districts.geojson`

| 항목 | 내용 |
|---|---|
| 쓰는 곳 | 여행 지역 선택 지도의 시도·시군구 윤곽(`lib/features/trip/screens/trip_step5_screen.dart`) |
| 출처 | OpenStreetMap 의 `boundary=administrative` 관계(admin_level 4·6), 해안선에서 만든 육지 다각형(osmdata.openstreetmap.de 의 simplified land polygons). © OpenStreetMap contributors |
| 이용조건 | [Open Database License(ODbL) 1.0](https://opendatacommons.org/licenses/odbl/1-0/). 원문: <https://www.openstreetmap.org/copyright>. 고지 파일 [`assets/geo/LICENSE-ODbL.md`](../assets/geo/LICENSE-ODbL.md) |
| 재배포 | 할 수 있다. 다만 이 두 파일은 저장소의 MIT 가 아니라 ODbL 을 따른다. 고쳐서 배포하면 결과도 ODbL 로 배포하고 출처를 밝힌다. 앱은 지도 위에 "© OpenStreetMap contributors" 를 표시한다 |
| 만드는 법 | `python3 -m pip install shapely pyshp` 후 `python3 scripts/build_geo.py [--cache 폴더]`. Overpass API 와 osmdata 에서 받으므로 네트워크가 필요하다 |
| 크기 | 파일마다 1MB 미만(스크립트가 단순화 허용 오차를 키워 가며 맞춘다) |

스키마(GeoJSON FeatureCollection, 경위도 WGS84). 두 파일 모두 최상위에 `attribution`·`license`·`source` 를 둔다.

| 파일 | 속성 | 뜻 |
|---|---|---|
| `provinces.geojson` | `CTPRVN_CD` | 시도 코드(두 자리, 앱 지역 목록 순서로 매긴 합성 번호) |
| | `CTP_KOR_NM`·`CTP_ENG_NM` | 시도 이름(앱 목록 표기)·영문 이름(OSM `name:en`) |
| `districts.geojson` | `SIG_CD` | 시군구 코드(시도 코드 + 세 자리). 앞 두 자리가 시도 코드와 같다 — 화면이 이 규칙으로 시도 안의 시군구를 고른다 |
| | `SIG_KOR_NM`·`SIG_ENG_NM` | 시군구 이름(앱 목록 표기)·영문 이름 |

스크립트가 하는 일:
1. 시군구 관계를 행정기관코드(`ref:KR:mois:admin`) 앞 두 자리로 시도에 묶는다. 코드가 없으면 광역 윤곽 안에 있는지로 정한다.
2. 앱 지역 목록(`lib/common/constants/korea_regions.dart`)에 있는 이름만 골라 앱 표기로 이름을 붙인다.
3. 영해까지 그려진 해안 쪽 경계를 육지 다각형으로 잘라 바다를 덜어 낸다.
4. 위상을 지키며 단순화하고, 약 10km² 보다 작은 섬 조각을 뺀다. 조각마다 지도 오버레이가 하나씩 생기기 때문이다.
5. 시도 윤곽은 단순화한 시군구를 합쳐 만든다.

한계:
- 받을 때의 OSM 상태를 따른다. 다시 만들면 결과가 조금씩 달라질 수 있다.
- 앱 지역 목록은 서버가 받는 표기를 쓴다. 개칭 전 시도 이름(강원도·전라북도)과 개편 전 시군구 목록이다. OSM 이 이미 개편된 구역으로 바뀐 곳은 이렇게 다룬다.
  - 인천광역시 서구는 OSM 의 서해구·검단구를 합쳐 쓴다.
  - 인천광역시 중구·동구는 OSM 에서 영종구·제물포구로 바뀌어 되돌려 나눌 수 없어 윤곽이 없다. 그 두 곳은 지도 윤곽 없이 목록으로만 고른다.
- 해안선은 저해상도용으로 단순화된 육지 다각형을 쓴다. 작은 섬과 해안의 세부는 실제와 다르다.
- 코드(`CTPRVN_CD`·`SIG_CD`)는 행정표준코드가 아니라 이 앱 안에서만 쓰는 합성 번호다.

### 지역 목록 — `lib/common/constants/korea_regions.dart`
시도 17개·시군구 229개의 이름 목록이다. 서버(map-project-user)가 받는 표기를 그대로 쓴다. 이름만 담은 사실 정보다.

### 그림 자산 — `assets/images/`, `assets/svg/`, `assets/icon/`, 플랫폼 아이콘
날씨·교통수단 그림, 캐릭터, 로고, 앱 아이콘은 이 프로젝트 팀이 만들었다. 저장소의 MIT 라이선스를 따른다. 로그인 말풍선·글 아이콘도 직접 그린 중립 아이콘이다. 외부 회사의 로고·배지는 넣지 않는다.

## 빌드 때 받는 자료

### 글꼴 Pretendard — `assets/fonts/`(git 에서 제외)

| 항목 | 내용 |
|---|---|
| 쓰는 곳 | 앱 전체 글꼴(`pubspec.yaml` 의 `fonts`, `lib/app.dart`) |
| 출처 | [orioncactus/pretendard](https://github.com/orioncactus/pretendard) v1.3.9 의 `PretendardVariable.ttf`, Copyright (c) Kil Hyung-jin |
| 이용조건 | [SIL Open Font License 1.1](https://openfontlicense.org), 예약 글꼴 이름 "Pretendard" |
| 받는 법 | `sh scripts/fetch_fonts.sh`. 태그 고정 주소에서 글꼴과 라이선스 원문(`OFL.txt`)을 받아 sha256 을 확인한다. 배포처 파일이 바뀌면 멈춘다 |
| 왜 저장소에 없나 | 6.7MB 라 저장소에 넣지 않는다. 원본을 그대로 받으므로 글꼴 이름을 바꾸지 않는다. 라이선스 원문은 글꼴과 함께 앱 자산에 실린다 |
| 주의 | `flutter pub get`·`flutter test`·빌드보다 먼저 실행해야 한다. CI 도 같은 순서로 돈다(네트워크 필요) |

## 실행 중에 보여 주기만 하는 자료

앱은 아래 자료를 저장소에 담지 않고, 기기에 따로 쌓아 두지도 않는다. 모두 서버(map-project-user)를 거쳐 받고, 서버 쪽 키와 이용조건은 그 서비스가 다룬다.

| 자료 | 앱에서의 처리 |
|---|---|
| 장소 사진 | 장소 상세에서 '사진 보기'를 누를 때만 받는다. 제공자 표기와 신고 링크를 함께 보이고, 받기 전에는 원본 지도 링크만 둔다 |
| 블로그 후기 발췌·요약 | 장소 상세에서 목록으로 보인다. 요약은 외부 AI 전송 동의 뒤에만 만든다 |
| 지도 타일 | 지도 SDK 가 직접 받는다. 키는 빌드하는 사람이 넣는다 |
| 날씨·대중교통·공유 자전거·킥보드 | 서버가 공공·외부 API 를 대신 불러 준 결과를 보인다 |

## 시험 데이터
시험의 주소·계정·좌표·시각은 모두 합성값이다(`*.example.test`, `example.com`, 고정된 가짜 날짜). 실제 사용자나 장소 데이터는 없다.

## 비공개 운영 자료와의 비호환
- 행정경계 파일은 예전 비공개본의 파일과 출처·코드 체계가 다르다. 예전 코드(행정표준코드)와 호환되지 않는다.
- 번들 ID·URL 스킴이 예전 비공개 운영 앱과 다르다. 기기에 남은 예전 앱의 저장 자료를 읽지 않는다.
