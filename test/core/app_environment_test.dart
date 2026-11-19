import 'package:flutter_test/flutter_test.dart';
import 'package:map_service_client/core/config/app_environment.dart';

void main() {
  test('default test app cannot share the production native identity', () {
    expect(AppEnvironment.name, 'test');
    expect(AppEnvironment.applicationId, 'map.project.client.dev');
    expect(AppEnvironment.kakaoNativeAppKey, isEmpty);
    expect(AppEnvironment.inviteScheme, 'mapproject-dev');
    expect(
      AppEnvironment.policyUrl('privacy.html').toString(),
      'https://web.example.test/legal/privacy.html',
    );
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
