# 0008. 빌드 환경마다 앱 신원을 나누고, 네이티브 설정을 매 빌드에서 대조한다

## 맥락
번들 ID·초대 스킴·카카오 복귀 스킴·앱 링크 도메인은 Dart 빌드값과 Android·iOS 네이티브 설정에 함께 있다. 한쪽만 바뀌면 앱은 뜨지만 로그인 복귀와 초대 링크만 조용히 실패한다. 시험 빌드와 운영 빌드가 같은 신원을 쓰면 한 기기에 같이 깔 수 없고, 링크가 엉뚱한 앱을 연다.

## 선택지
1. 신원을 한 벌로 두고 사람이 맞춘다.
2. 환경(`test`·`prod`)마다 신원을 고정하고, 빌드값으로 덮어쓸 수 없게 한다. iOS 는 매 Xcode 빌드에서 두 쪽을 대조한다.

## 결정
2.
- 시험 빌드는 `map.project.client.dev`·`mapproject-dev`, 운영 빌드는 `map.project.client`·`mapproject` 다.
- Android 는 Gradle 이 dart-define 에서 신원을 계산한다. iOS 는 `ios/Flutter/verify_native_environment.py` 가 빌드 단계에서 xcconfig 와 Dart 빌드값을 대조하고, 어긋나면 빌드를 멈춘다.

## 결과
- 다른 환경으로 iOS 를 빌드할 때는 `--print-xcconfig` 로 `NativeEnvironment.xcconfig` 를 만든다.
- 초대 origin 을 주지 않은 빌드의 앱 링크 도메인 자리는 예약 도메인 `invite.example.invalid` 로 채운다. 도메인 검증이 일어나지 않고 앱 전용 스킴만 쓰인다.
- 스토어에 올리는 사람은 자기 번들 ID 를 쓰게 된다. 이 이름들은 소유한 도메인을 뜻하지 않는다.
- 관련 커밋: [`0610b14`](https://github.com/we-meet-trip/map-project-client/commit/0610b147cdd87202453a7ed09872d030eacd24b4)
