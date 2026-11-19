/// Native identity and public URLs use the same build environment as AppConfig.
/// Production values never fall back to the test hosting domain.
class AppEnvironment {
  AppEnvironment._();

  static const name = String.fromEnvironment('APP_ENV', defaultValue: 'test');
  static const applicationId = name == 'test'
      ? 'map.project.client.dev'
      : 'map.project.client';
  static const inviteScheme = name == 'test' ? 'mapproject-dev' : 'mapproject';
  /// 카카오 SDK 가 쓰는 네이티브 앱 키. 커스텀 스킴(kakao{키}://oauth)에 그대로
  /// 실리는 공개 값이라 앱에 들어간다. 카카오는 이 키를 번들 ID 에 묶어 통제한다.
  static const kakaoNativeAppKey = String.fromEnvironment('KAKAO_NATIVE_APP_KEY');
  static const inviteOrigin = String.fromEnvironment(
    'INVITE_LINK_ORIGIN',
    defaultValue: name == 'test' ? 'https://web.example.test' : '',
  );
  static const publicOrigin = String.fromEnvironment(
    'PUBLIC_SITE_ORIGIN',
    defaultValue: name == 'test' ? 'https://web.example.test' : '',
  );

  static Uri policyUrl(String document) {
    if (!const {
      'privacy.html',
      'terms.html',
      'location-terms.html',
      'support.html',
      'delete-account.html',
    }.contains(document)) {
      throw ArgumentError.value(document, 'document');
    }
    final origin = Uri.tryParse(publicOrigin);
    if (!const {'test', 'prod'}.contains(name) ||
        origin == null ||
        origin.scheme != 'https' ||
        origin.host.isEmpty ||
        origin.userInfo.isNotEmpty ||
        (origin.path.isNotEmpty && origin.path != '/') ||
        origin.hasQuery ||
        origin.hasFragment ||
        (name == 'prod' &&
            const {
              'web.example.test',
              'web.example.test',
              'api.example.test',
              'api-alt.example.test',
            }.contains(origin.host))) {
      throw StateError('Invalid PUBLIC_SITE_ORIGIN for the app environment');
    }
    return origin.replace(path: '/legal/$document');
  }
}
