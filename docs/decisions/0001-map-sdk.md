# 0001. 지도 SDK 로 Google Maps 를 쓴다

## 맥락
지도는 일정 경로, 지역 선택, 장소 탐색, 이동수단 위치 화면의 바탕이다. 같은 코드로 iOS·Android·웹을 모두 그려야 하고, 장소 사진 같은 Google 장소 데이터도 지도 옆에 보인다.

## 선택지
1. 카카오 지도: 공식 Flutter 플러그인이 없어 비공식 플러그인에 기대야 했다.
2. 네이버 지도(`flutter_naver_map`): Android·iOS 전용이라 웹은 따로 JavaScript 어댑터를 만들어야 했다. 지도 식별자 인증이 기기 등록값에 묶여 환경마다 맞추기 까다로웠다.
3. Google Maps(`google_maps_flutter`): 공식 플러그인이 세 플랫폼을 지원하고, 플랫폼별 클라이언트 키로 인증한다.

## 결정
Google Maps 를 쓴다. 앞의 두 SDK 로 만든 코드는 지웠다.

## 결과
- 플랫폼마다 클라이언트 키를 빌드값(`CLIENT_GOOGLE_MAPS_ANDROID_API_KEY`·`_IOS_`·`_WEB_`)으로 넣는다. 키가 없으면 지도 없이 나머지 화면이 돈다.
- 웹은 조건부 import 로 웹 전용 로더를 쓴다(`lib/core/maps/map_loader_web.dart`). 네이버 지도 시절에 웹 지원 때문에 겪은 일은 [트러블슈팅](../troubleshooting.md)의 T-MAP-01 에 있다.
- 장소 데이터와 지도가 같은 제공자라, 이용조건을 한 곳만 보면 된다(해석).
- 관련 커밋: [`49333de`](https://github.com/we-meet-trip/map-project-client/commit/49333de795af84cdb24e5832a05191a210e1281c), [`0cb26b9`](https://github.com/we-meet-trip/map-project-client/commit/0cb26b9a530a198a0c953d0ec4d54d9cad062e98)
