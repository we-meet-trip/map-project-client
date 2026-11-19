# 0002. 외부 API 는 앱이 직접 부르지 않고 서버를 거친다

## 맥락
날씨, 지하철·대중교통 경로, 공유 자전거·킥보드 위치, 주소 검색은 공공·외부 API 의 키가 필요하다. 앱 꾸러미에 든 값은 누구나 꺼낼 수 있고, 키를 플랫폼마다 따로 들고 다녀야 한다.

## 선택지
1. 앱이 발급처를 직접 부른다(키를 앱에 넣는다).
2. 서버(map-project-user → map-project-hub)가 대신 부르고 앱은 결과만 받는다.

## 결정
2. 앱에는 기기에 묶어 제한할 수 있는 클라이언트 키(지도 SDK, 카카오 네이티브 앱 키)만 둔다. 나머지 외부 호출은 모두 서버 경유다.

## 결과
- 앱이 부르는 서버 주소가 하나(API origin)라 허용 origin 규칙 하나로 토큰과 요청을 지킬 수 있다([0003](0003-server-address-and-origins.md)).
- 서버가 멈추면 그 기능도 멈춘다. 앱은 실패를 '자료 없음'과 갈라 보인다.
- 이 결정 전에 키가 앱 꾸러미에 실렸던 일과 그 정리는 [트러블슈팅](../troubleshooting.md)의 T-SEC-02 에 있다.
- 관련 커밋: [`83aaa95`](https://github.com/we-meet-trip/map-project-client/commit/83aaa95cd1d69c1b1138e99b05af5429d3a6ff84), [`376bbda`](https://github.com/we-meet-trip/map-project-client/commit/376bbda97e7680d5c034216c985594c21810cc74)
