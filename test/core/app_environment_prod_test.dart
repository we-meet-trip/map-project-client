import 'package:flutter_test/flutter_test.dart';
import 'package:map_project_client/core/config/app_environment.dart';
import 'package:map_project_client/core/services/deep_link_service.dart';

void main() {
  group('production build identity', () {
    test('uses production native IDs and rejects test custom links', () {
      expect(AppEnvironment.applicationId, 'map.project.client');
      expect(AppEnvironment.kakaoNativeAppKey, isEmpty);
      expect(AppEnvironment.inviteScheme, 'mapproject');
      expect(
        DeepLinkService.routeOf(Uri.parse('mapproject://invite/TOK')),
        '/invite/TOK',
      );
      expect(
        DeepLinkService.routeOf(Uri.parse('mapproject-dev://invite/TOK')),
        isNull,
      );
      expect(
        DeepLinkService.routeOf(
          Uri.parse('https://invite.example.test/invite/TOK'),
        ),
        isNull,
      );
    });

    test('production without a policy site shows no policy links', () {
      expect(AppEnvironment.publicOrigin, isEmpty);
      expect(() => AppEnvironment.policyUrl('privacy.html'), throwsStateError);
    });
  }, skip: AppEnvironment.name != 'prod');
}
