import 'package:flutter_test/flutter_test.dart';
import 'package:map_project_client/core/config/app_environment.dart';

void main() {
  test('default test app cannot share the production native identity', () {
    expect(AppEnvironment.name, 'test');
    expect(AppEnvironment.applicationId, 'map.project.client.dev');
    expect(AppEnvironment.kakaoNativeAppKey, isEmpty);
    expect(AppEnvironment.inviteScheme, 'mapproject-dev');
    // 정책 사이트를 주지 않은 기본 빌드는 약관 링크를 만들지 않는다.
    expect(AppEnvironment.publicOrigin, isEmpty);
    expect(AppEnvironment.hasPublicSite, isFalse);
    expect(() => AppEnvironment.policyUrl('privacy.html'), throwsStateError);
    expect(AppEnvironment.inviteOrigin, isEmpty);
  });

  test('a configured policy site yields fixed document paths only', () {
    expect(
      AppEnvironment.policyUrl(
        'privacy.html',
        site: 'https://policy.example.test',
      ).toString(),
      'https://policy.example.test/legal/privacy.html',
    );
    for (final site in [
      'http://policy.example.test',
      'https://user@policy.example.test',
      'https://policy.example.test/sub',
      'https://policy.example.test?x=1',
    ]) {
      expect(
        () => AppEnvironment.policyUrl('privacy.html', site: site),
        throwsStateError,
        reason: site,
      );
    }
  });

  test('policy links cannot escape the approved document set', () {
    for (final document in [
      '../secret',
      'https://other.example',
      'privacy.html?x=1',
    ]) {
      expect(() => AppEnvironment.policyUrl(document), throwsArgumentError);
    }
  });
}
