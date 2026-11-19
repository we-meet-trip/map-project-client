/// Native identity and public URLs use the same build environment as AppConfig.
///
/// 초대 링크 origin 과 정책 문서 사이트는 기본값이 비어 있다. 배포하는 사람이
/// 자기 주소를 빌드값으로 줄 때만 https 초대 링크와 약관·개인정보 화면이 켜진다.
class AppEnvironment {
  AppEnvironment._();

  static const name = String.fromEnvironment('CLIENT_APP_ENV', defaultValue: 'test');
  static const applicationId = name == 'test'
      ? 'map.project.client.dev'
      : 'map.project.client';
  static const inviteScheme = name == 'test' ? 'mapproject-dev' : 'mapproject';

  /// 카카오 SDK 가 쓰는 네이티브 앱 키. 커스텀 스킴(kakao{키}://oauth)에 그대로
  /// 실리는 공개 값이라 앱에 들어간다. 카카오는 이 키를 번들 ID 에 묶어 통제한다.
  static const kakaoNativeAppKey = String.fromEnvironment(
    'CLIENT_KAKAO_NATIVE_APP_KEY',
  );
  static const inviteOrigin = String.fromEnvironment('CLIENT_INVITE_LINK_ORIGIN');
  static const publicOrigin = String.fromEnvironment('CLIENT_PUBLIC_SITE_ORIGIN');

  static const _documents = {
    'privacy.html',
    'terms.html',
    'location-terms.html',
    'support.html',
    'delete-account.html',
  };

  /// 정책 문서 사이트를 줬는지. 주지 않았으면 약관·정책 메뉴를 감춘다.
  static bool get hasPublicSite => _siteOrigin(publicOrigin) != null;

  static Uri? _siteOrigin(String value) {
    final origin = Uri.tryParse(value);
    if (!const {'test', 'prod'}.contains(name) ||
        origin == null ||
        origin.scheme != 'https' ||
        origin.host.isEmpty ||
        origin.userInfo.isNotEmpty ||
        (origin.path.isNotEmpty && origin.path != '/') ||
        origin.hasQuery ||
        origin.hasFragment) {
      return null;
    }
    return origin;
  }

  static Uri policyUrl(String document, {String site = publicOrigin}) {
    if (!_documents.contains(document)) {
      throw ArgumentError.value(document, 'document');
    }
    final origin = _siteOrigin(site);
    if (origin == null) {
      throw StateError('CLIENT_PUBLIC_SITE_ORIGIN is not configured for this build');
    }
    return origin.replace(path: '/legal/$document');
  }
}
