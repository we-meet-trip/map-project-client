# 계약

앱이 부르는 상대는 사용자 BFF [map-project-user](https://github.com/we-meet-trip/map-project-user) 하나다. 경로·필드의 정의는 그 저장소의 `docs/contracts.md` 가 기준이고, 여기에는 앱이 기대하는 것과 앱이 정의하는 것을 적는다.

## 전송

| 항목 | 내용 | 근거 |
|---|---|---|
| 기준 주소 | `AppConfig` 가 정한 API origin(로컬 기본값 `http://localhost:8080`) | `lib/core/config/app_config.dart` |
| 인증 | `Authorization: Bearer <access token>`. 401 이면 토큰을 한 번 갱신하고 다시 보낸다(인증 경로 제외) | `lib/core/api/api_client.dart` |
| 본문 | JSON(UTF-8) | 같은 파일 |
| 오류 | 응답 본문의 `code`(없으면 `error`)와 `message`(없으면 `detail`)를 읽어 `ApiException` 으로 바꾼다 | `api_client.dart:234-235` |
| 실시간 채팅 | STOMP over WebSocket, `ws(s)://<API origin>/ws/chat`, 연결 상한 10초 | `lib/core/api/chat_realtime_service.dart` |
| Vision | WebSocket `ws(s)://<API origin>/ws/vision`. debug 빌드에서만 `CLIENT_VISION_SERVER_HOST` 로 다른 호스트를 쓸 수 있다 | `lib/features/vision/services/vision_ws_service.dart` |

## 앱이 부르는 경로

| 묶음 | 경로 |
|---|---|
| 인증 | `POST /api/v1/auth/signup`·`/login`·`/logout`·`/token/refresh`·`/kakao/callback`·`/apple/callback`, `GET /api/v1/auth/apple/nonce` |
| 사용자 | `GET·PATCH·DELETE /api/v1/users/me` |
| 서비스 이용 동의 | `GET·POST /api/v1/consents` |
| 외부 AI 전송 동의 | `GET /api/v1/consents/ai`, `POST·DELETE /api/v1/consents/ai/{기능}` |
| 여행 추천 | `POST /api/v1/trip/generate`, `/replan`, `/research`, `/route` |
| 일정 | `GET·POST /api/v1/schedules`, `GET·PUT·DELETE /api/v1/schedules/{id}`, `POST /api/v1/schedules/{id}/start`, `POST /api/v1/schedules/{id}/weather-alert/dismiss` |
| 장소 | `GET /api/v1/places/search`, `/address`, `/photos` |
| 후기 | `GET /api/v1/reviews`, `GET /api/v1/reviews/summary`(저장된 요약 조회), `POST /api/v1/reviews/summary`(외부 AI 전송 동의 뒤 요약 생성) |
| 날씨 | `GET /api/v1/weather/home`, `/forecast` |
| 대중교통 | `/api/v1/transit/routes`, `/routes/lane`, `/routes/walk`, `/subway` |
| 이동수단 | `GET /api/v1/mobility/bike-stations`, `/pm-vehicles` |
| 채팅·초대 | `/api/v1/chat/...`(방·메시지·초대 발급) |
| 신고·차단 | `/api/v1/moderation/...` |

## 서버가 정하고 앱이 받는 값

### 정책 판
- 이용약관·개인정보·외부 AI 동의의 판(`terms_version`·`privacy_version`·`policy_version`)은 서버가 정한다. 공개본 서버의 값은 `1.0.0` 이다.
- 앱은 판 문자열의 뜻을 해석하지 않는다. 형식(`^[A-Za-z0-9][A-Za-z0-9._-]{0,31}$`, `lib/core/state/service_consent_store.dart`)만 확인하고, 동의할 때 받은 값을 그대로 돌려보낸다. 판이 바뀌어도 앱을 다시 낼 필요가 없다.
- 서비스 이용 동의: `POST /api/v1/consents` 본문은 `{terms_version, privacy_version, is_18_or_older: true, terms_accepted: true, privacy_accepted: true}`.
- 외부 AI 전송 동의: `POST /api/v1/consents/ai/{기능}` 본문은 `{policy_version, accepted: true, include_location, expected_revision}`. 철회는 `DELETE` 에 `expected_revision` 질의 인자를 붙인다. 판이 맞지 않으면 서버가 409 `POLICY_VERSION_MISMATCH` 로 답하고, 앱은 다시 확인하라고 안내한다.

### 초대 링크
- 발급 응답은 `{token, url, expires_at}` 이다. `url` 은 user 의 초대 기준 주소 + 토큰이다.
- **배포자는 user 의 초대 기준 주소와 client 의 초대 origin(`CLIENT_INVITE_LINK_ORIGIN`)을 같은 origin 으로 준다. user 의 기준 주소가 비어 있으면 초대 응답의 url 은 null 이고 token 만 유효하다. 이때 client 는 token 으로 앱 전용 주소(`<스킴>://invite/<token>`)를 만들어 공유하며, 이 주소는 앱이 설치된 기기에서만 열린다.**
- 앱이 받는 링크(`lib/core/services/deep_link_service.dart`):
  - `https://<CLIENT_INVITE_LINK_ORIGIN>/invite/<token>` — origin 을 줬을 때만
  - `<스킴>://invite/<token>` — 스킴은 환경마다 `mapproject-dev`·`mapproject`
  - 토큰은 `[A-Za-z0-9_-]{1,256}` 이다. 사용자 정보·질의·조각·추가 경로·포트가 붙은 링크와 다른 환경의 스킴은 받지 않는다.

### 원격 설정 문서(선택)
`CLIENT_APP_CONFIG_URL` 로 위치를 주면 앱이 시작할 때 읽는 JSON 이다.

```json
{"environment": "prod", "api_base_url": "https://api.example.com"}
```

- `environment` 가 앱 빌드 환경과 같아야 한다. 시험 환경에서만 생략할 수 있다.
- `api_base_url` 은 `CLIENT_API_ALLOWED_ORIGINS` 안의 https origin 이어야 한다.
- 조회 상한은 3초이고, 실패하면 캐시나 기본값으로 시작한 뒤 뒤에서 다시 묻는다.

## 앱이 정의하는 값

| 값 | test(기본) | prod | 소비 |
|---|---|---|---|
| 번들 ID / applicationId | `map.project.client.dev` | `map.project.client` | user 의 Apple 로그인 클라이언트 ID 설정 |
| 초대 URL 스킴 | `mapproject-dev` | `mapproject` | 초대 링크를 만드는 쪽(앱 자신) |
| 앱 링크 도메인(초대 origin 이 없을 때) | `invite.example.invalid` | `invite.example.invalid` | 매니페스트·entitlements 자리 채움 |

빌드값 이름(dart-define)은 [`.env.example`](../.env.example)에 있다. 모두 `CLIENT_` 접두를 쓴다.

## 길이·개수 한도

| 대상 | 한도 | 근거 |
|---|---|---|
| 보내지 못한 채팅 메시지 보관 | 방마다 20개 | `lib/features/chat/providers/chat_room_detail_provider.dart` |
| 닉네임 | 2~8자 | `lib/features/auth/screens/signup_step1_screen.dart` |
| 비밀번호 | 8자 이상 | `lib/features/auth/screens/signup_step4_screen.dart` |
| 대중교통 구간 | 20구간을 넘는 경로 응답은 쓰지 않는다 | `lib/core/api/transit_route_options_service.dart` |
