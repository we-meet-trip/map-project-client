# 다이어그램 근거표

그림의 노드와 엣지마다 근거를 적는다. 원본은 `docs/diagrams/src/*.dot`, 다시 그리기는 `sh scripts/render_diagrams.sh`.

## app-structure (앱 구조)

| 그림 | 요소 | 주장 | 근거 file:line | 확인 방법 |
|---|---|---|---|---|
| app-structure | 노드 lib/features 묶음 | 화면은 기능별 폴더에 있다 | `lib/features/`(trip·place_explore·chat·invite·vision·auth·mypage) | 폴더 목록 |
| app-structure | 노드 서버 호출 api | 화면의 서버 호출은 공통 통로 `ApiClient` 를 지난다 | `lib/core/api/api_client.dart:50`(상한), `:122`(인증 헤더) | 코드 읽기 |
| app-structure | 노드 지도 어댑터 | 지도 위젯 `AppMap` 이 SDK 를 감싼다 | `lib/core/maps/map_adapter.dart:246` | 코드 읽기 |
| app-structure | 노드 주소·신원 결정 | 서버 주소와 앱 신원을 정한다 | `lib/core/config/app_config.dart:62`, `lib/core/config/app_environment.dart` | 코드 읽기 |
| app-structure | 노드 전역 상태 | 로그인 상태와 토큰을 가진다 | `lib/core/state/auth_store.dart:27` | 코드 읽기 |
| app-structure | 노드 기기 저장 | Hive 상자와 secure storage 를 쓴다 | `lib/data/local/local_box.dart`, `lib/data/local/chat_outbox_store.dart:13` | 코드 읽기 |
| app-structure | 노드 map-project-user | 앱이 부르는 유일한 서버 | `lib/core/config/endpoint_policy.dart`(허용 origin 하나의 목록) | 코드 읽기 |
| app-structure | 노드 Google Maps SDK | 외부 지도 SDK | `pubspec.yaml`(`google_maps_flutter`) | 의존성 목록 |
| app-structure | 엣지 화면 → api "모든 화면" | 기능 화면은 `lib/core/api` 서비스를 부른다 | 예: `lib/features/place_explore/widgets/place_bottom_sheet.dart`(`PlacePhotoApiService`) | 코드 읽기 |
| app-structure | 엣지 장소 탐색 → 지도 어댑터 | 지도 화면은 어댑터를 쓴다 | `lib/features/trip/screens/trip_step5_screen.dart`(`AppMap`) | 코드 읽기 |
| app-structure | 엣지 api → config "기준 주소" | 요청 주소는 `AppConfig` 가 정한 origin 이다 | `lib/core/config/app_config.dart` | 코드 읽기 |
| app-structure | 엣지 api → state "토큰" | 요청에 저장된 토큰을 붙이고 401 이면 갱신한다 | `lib/core/api/api_client.dart:122`, `:159-168` | 코드 읽기 |
| app-structure | 엣지 state → 기기 저장 | 토큰은 secure storage 에 둔다 | `lib/core/state/auth_store.dart:27` | 코드 읽기 |
| app-structure | 엣지 대화방 → 기기 저장 "보낼 메시지" | 서버 확인 전 메시지를 암호화해 둔다 | `lib/data/local/chat_outbox_store.dart:1-13` | 코드 읽기 |
| app-structure | 엣지 api → BFF "HTTPS · WebSocket" | REST 와 `/ws/chat`·`/ws/vision` | `lib/core/api/chat_realtime_service.dart:255`, `lib/features/vision/services/vision_ws_service.dart:65` | 코드 읽기 |
| app-structure | 엣지 지도 어댑터 → Google Maps SDK "클라이언트 키" | 플랫폼별 키를 빌드값으로 받는다 | `lib/core/maps/map_bootstrap.dart:10-16`, `ios/Runner/AppDelegate.swift:20`, `android/app/build.gradle.kts:99` | 코드 읽기 |

## screen-flow (주요 화면 흐름)

| 그림 | 요소 | 주장 | 근거 file:line | 확인 방법 |
|---|---|---|---|---|
| screen-flow | 노드 시작 /splash | 첫 경로 | `lib/core/router/app_router.dart:114` | 코드 읽기 |
| screen-flow | 엣지 시작 → 권한 안내 "처음 한 번" | 안내를 보지 않았으면 먼저 보낸다 | `lib/core/router/app_router.dart:88-93` | 코드 읽기 |
| screen-flow | 엣지 권한 안내 → 로그인 | 로그인 안 한 사용자는 `/auth` 로 | `lib/core/router/app_router.dart:94-95` | 코드 읽기 |
| screen-flow | 노드 로그인 | 이메일·카카오·Apple(iOS) | `lib/features/auth/screens/auth_screen.dart:139-160` | 코드 읽기 |
| screen-flow | 엣지 로그인 → 서비스 이용 동의 "동의 전" | 동의 전이면 동의 화면으로 | `lib/core/router/app_router.dart:96-104`, `:131-136` | 코드 읽기 |
| screen-flow | 노드 하단 탭 | 홈·여행·저장·대화방·마이페이지 탭 | `lib/core/router/app_router.dart:223-226`, `:229`, `:235`, `:299`, `:377`, `:416` | 코드 읽기 |
| screen-flow | 엣지 탭 → 카메라 질문 | 탭 화면 위의 떠 있는 버튼으로 연다 | `lib/common/layout/main_layout.dart:20`, `lib/common/widgets/draggable_vision_button.dart:92` | 코드 읽기 |
| screen-flow | 엣지 여행 → 여행 만들기 | 추천·직접 계획·랜덤 미션 갈래 | `lib/core/router/app_router.dart:239`, `:250-259` | 코드 읽기 |
| screen-flow | 노드 외부 AI 전송 동의 | 추천 결과를 만들기 전에 기능별로 묻는다(기본 없음) | `lib/common/widgets/external_ai_consent.dart:45`, `:121`, `lib/features/trip/screens/trip_created_screen.dart:374` | 코드 읽기 |
| screen-flow | 엣지 여행 만들기 → 일정 결과 "직접 계획" | 직접 계획은 외부 AI 전송 없이 만든다 | `lib/core/router/app_router.dart:250-256`, `lib/features/trip/screens/manual_plan_entry_screen.dart`·`plan_flow_screen.dart`(추천 호출·AI 동의 0건) | 코드 검색 |
| screen-flow | 엣지 여행 → 장소 탐색 | 장소 탐색 경로 | `lib/core/router/app_router.dart:263-285` | 코드 읽기 |
| screen-flow | 노드 사진 보기(누를 때만) | 시트를 여는 것만으로는 사진을 청하지 않는다 | `lib/features/place_explore/widgets/place_bottom_sheet.dart:92`, `:347-348` | 시험 `test/features/place_explore/place_detail_states_test.dart` |
| screen-flow | 엣지 저장한 일정 → 일정 상세 | 상세·편집·길안내 | `lib/core/router/app_router.dart:303-358` | 코드 읽기 |
| screen-flow | 엣지 대화방 → /chat/:id | 방 화면 | `lib/core/router/app_router.dart:387` | 코드 읽기 |
| screen-flow | 엣지 초대 링크 → 대화방 "토큰 확인 뒤" | 초대 수락 뒤 그 방으로 간다 | `lib/core/router/app_router.dart:155`, `lib/features/invite/screens/invite_handler_screen.dart:77` | 코드 읽기 |

## sdk-boundary (외부 SDK 경계)

| 그림 | 요소 | 주장 | 근거 file:line | 확인 방법 |
|---|---|---|---|---|
| sdk-boundary | 노드 map-project-client | 기기 안의 앱 | `lib/main.dart` | — |
| sdk-boundary | 엣지 앱 → 기기 저장 | Hive·secure storage | `lib/data/local/local_box.dart`, `lib/core/state/auth_store.dart:27` | 코드 읽기 |
| sdk-boundary | 엣지 앱 → 기기 기능 "권한" | 위치·카메라·음성·나침반·사진 | `pubspec.yaml`(geolocator·camera·speech_to_text·flutter_compass·image_picker), `lib/features/saved/screens/navigation_screen.dart:219` | 의존성·코드 읽기 |
| sdk-boundary | 엣지 앱 → Sign in with Apple | iOS 에서만 버튼을 보인다 | `lib/features/auth/screens/auth_screen.dart:142-143` | 코드 읽기 |
| sdk-boundary | 엣지 앱 → 카카오 SDK "네이티브 앱 키" | 키가 있을 때만 SDK 를 켠다 | `lib/main.dart:31-33`, `android/app/build.gradle.kts`(kakaoNativeAppKey) | 코드 읽기 |
| sdk-boundary | 엣지 앱 → Google Maps SDK "클라이언트 키" | 키가 있을 때만 SDK 에 넣는다 | `ios/Runner/AppDelegate.swift:20`, `lib/core/maps/map_bootstrap.dart` | 코드 읽기 |
| sdk-boundary | 엣지 앱 → BFF "HTTPS /api/v1 · /ws/chat · /ws/vision" | 앱의 서버 통신은 BFF 하나로 간다 | `lib/core/api/api_client.dart`, `lib/core/api/chat_realtime_service.dart:255`, `lib/features/vision/services/vision_ws_service.dart:65` | 코드 읽기 |
| sdk-boundary | 묶음 BFF 뒤 | 앱은 agent·hub·yolo 주소를 모른다 | `lib/core/config/endpoint_policy.dart`(허용 origin 은 BFF 하나), [contracts.md](../contracts.md) | 코드 읽기 |
| sdk-boundary | 엣지 BFF → agent·hub·yolo | BFF 가 추천·외부 데이터·비전을 중계한다 | map-project-user 의 `docs/contracts.md`, map-project-infra 의 전체 그림 | 다른 저장소 문서 |
| sdk-boundary | 노드 외부 AI 처리자(기본 꺼짐) | 기능별 동의 뒤에만 입력이 간다 | `lib/common/widgets/external_ai_consent.dart:45`, `:121` | 시험 `test/features/moderation/external_ai_persisted_consent_test.dart` |
| sdk-boundary | 엣지 hub → 공공·외부 API | 날씨·교통·장소 키는 서버 쪽에만 있다 | [decisions/0002](../decisions/0002-external-apis-via-server.md) | 문서 |
