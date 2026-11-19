import 'package:url_launcher/url_launcher.dart';

/// 문의·신고 메일의 수신 주소. 빌드할 때 `--dart-define=SUPPORT_EMAIL=...` 로 넣는다.
/// 공개본 기본값은 비어 있고, 비어 있으면 메일 문의 버튼을 감춘다.
const String supportEmail = String.fromEnvironment('SUPPORT_EMAIL');

/// 문의 메일 주소를 줬는지.
const bool hasSupportEmail = supportEmail != '';

/// 기본 메일 앱을 문의 양식으로 연다. 열 수 있으면 true.
///
/// 쿼리는 직접 인코딩해 조립한다 — Uri(queryParameters:)는 공백을 +로
/// 바꾸는데, 메일 앱은 그 +를 문자 그대로 보여 준다.
Future<bool> launchSupportMail({
  required String subject,
  String body = '',
}) async {
  if (!hasSupportEmail) return false;
  final query =
      'subject=${Uri.encodeComponent(subject)}'
      '${body.isEmpty ? '' : '&body=${Uri.encodeComponent(body)}'}';
  final uri = Uri.parse('mailto:$supportEmail?$query');
  try {
    return await launchUrl(uri, mode: LaunchMode.externalApplication);
  } on Exception {
    return false;
  }
}
