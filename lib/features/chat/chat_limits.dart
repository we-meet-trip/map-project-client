/// 채팅 메시지 한 건의 최대 길이(UTF-16 코드 단위, Dart `String.length` 와 같다).
///
/// 서버(map-project-user)가 이보다 긴 메시지를 거절한다. 서비스 사이 길이 약속은
/// 보내는 쪽이 지키므로, 입력창과 전송 경로가 미리 막는다.
const int kChatMessageMaxLength = 2000;
