import 'package:flutter_test/flutter_test.dart';
import 'package:map_project_client/core/api/invite_api_service.dart';
import 'package:map_project_client/core/services/deep_link_service.dart';
import 'package:map_project_client/data/repositories/api_invite_link_repository.dart';

/// 서버에 초대 기준 주소가 없으면 응답의 url 은 null 이고 token 만 온다(user 와의 계약).
/// 그때 앱은 토큰으로 앱 전용 주소를 만들고, 그 주소는 앱의 딥링크 해석과 맞아야 한다.
void main() {
  test('null url parses as empty and keeps the token', () {
    final issued = InviteLinkResponse.fromJson({
      'token': 'TOK_1',
      'url': null,
      'expires_at': null,
    });
    expect(issued.url, isEmpty);
    expect(issued.token, 'TOK_1');
  });

  test('app link for a token opens the invite route', () {
    final link = ApiInviteLinkRepository.appLinkFor('TOK_1');
    expect(link, 'mapproject-dev://invite/TOK_1');
    expect(DeepLinkService.routeOf(Uri.parse(link)), '/invite/TOK_1');
  });

  test('malformed tokens yield no link', () {
    for (final token in ['', 'a/b', 'a b', 'x' * 257]) {
      expect(ApiInviteLinkRepository.appLinkFor(token), isEmpty, reason: token);
    }
  });
}
