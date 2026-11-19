import '../../core/api/invite_api_service.dart';
import '../../core/config/app_environment.dart';
import 'invite_link_repository.dart';

/// 서버가 발급한 초대 링크를 전달하는 발급기.
///
/// https 주소는 클라이언트에서 조립하지 않는다. 기준 주소는 서버 설정이고 앱 링크
/// 검증도 그 주소를 기준으로 걸려 있다. 양쪽에서 따로 만들면 배포처가 바뀔 때
/// 한쪽만 따라가서, 링크가 앱 대신 브라우저로 열리는 형태로 조용히 어긋난다.
///
/// 서버에 기준 주소가 없으면 응답의 url 은 null 이고 token 만 온다. 그때는 앱 전용
/// 주소(`<스킴>://invite/<token>`)를 만든다 — 앱이 설치된 기기에서만 열린다.
class ApiInviteLinkRepository implements InviteLinkRepository {
  ApiInviteLinkRepository({InviteApiService? api})
    : _api = api ?? InviteApiService.instance;

  final InviteApiService _api;

  static final _token = RegExp(r'^[A-Za-z0-9_-]{1,256}$');

  /// 서버가 준 url 이 비었을 때 쓰는 앱 전용 초대 주소. 토큰 모양이 틀리면 빈 문자열.
  static String appLinkFor(
    String token, {
    String scheme = AppEnvironment.inviteScheme,
  }) => _token.hasMatch(token) ? '$scheme://invite/$token' : '';

  @override
  Future<InviteLink> generateInviteLink(int roomId) async {
    final issued = await _api.generate(roomId);
    final url = issued.url.isNotEmpty ? issued.url : appLinkFor(issued.token);
    return InviteLink(url: url, expiresAt: issued.expiresAt);
  }
}
