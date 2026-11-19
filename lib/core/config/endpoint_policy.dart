/// The API origin is also the token storage boundary. Paths and userinfo cannot
/// select a different API below an otherwise allowed host.
///
/// 기본값에는 어떤 서버 주소도 없다. 배포하는 사람이 빌드값으로 허용 origin 과
/// (쓴다면) 원격 설정 주소를 넣는다. 운영 빌드는 허용 origin 을 반드시 직접 줘야 한다.
class EndpointPolicy {
  const EndpointPolicy({
    required this.environment,
    required this.allowedOrigins,
    required this.configUrl,
    required this.explicitOrigins,
  });

  final String environment;
  final String allowedOrigins;

  /// 원격 설정 문서 주소. 비어 있으면 원격 조회를 하지 않는다.
  final String configUrl;
  final bool explicitOrigins;

  List<String> get _origins => allowedOrigins
      .split(',')
      .map((s) => s.trim())
      .where((s) => s.isNotEmpty)
      .toList();

  bool get hasRemoteConfig => configUrl.isNotEmpty;

  bool get valid {
    if (environment != 'test' && environment != 'prod') return false;
    if (hasRemoteConfig) {
      if (configUrl.contains(RegExp(r'[\s\\]'))) return false;
      final config = Uri.tryParse(configUrl);
      if (config == null || !_safeHttps(config)) return false;
    }
    final origins = _origins;
    if (origins.any((s) => normalize(s, requireHttps: true) == null)) {
      return false;
    }
    if (environment == 'prod' && (!explicitOrigins || origins.isEmpty)) {
      return false;
    }
    return true;
  }

  String? trusted(String? raw) {
    if (!valid) return null;
    final value = normalize(raw, requireHttps: true);
    if (value == null) return null;
    final allowed = _origins.map((s) => normalize(s, requireHttps: true));
    return allowed.contains(value) ? value : null;
  }

  String? remote(dynamic decoded) {
    if (!valid || decoded is! Map<String, dynamic>) return null;
    final declaredEnvironment = decoded['environment'];
    // Only the existing test document may omit this field during transition.
    if ((environment == 'prod' || declaredEnvironment != null) &&
        declaredEnvironment != environment) {
      return null;
    }
    final value = decoded['api_base_url'];
    return value is String ? trusted(value) : null;
  }

  static bool _safeHttps(Uri uri) {
    try {
      return uri.scheme == 'https' &&
          uri.host.isNotEmpty &&
          uri.userInfo.isEmpty &&
          !uri.hasQuery &&
          !uri.hasFragment &&
          uri.port > 0 &&
          uri.port <= 65535;
    } on FormatException {
      return false;
    }
  }

  static String? normalize(String? raw, {bool requireHttps = false}) {
    if (raw == null || raw.isEmpty || raw.contains(RegExp(r'[\s\\]'))) {
      return null;
    }
    try {
      final uri = Uri.parse(raw);
      if (uri.scheme != 'http' && uri.scheme != 'https') return null;
      if (requireHttps && !_safeHttps(uri)) return null;
      if (uri.host.isEmpty ||
          uri.userInfo.isNotEmpty ||
          uri.hasQuery ||
          uri.hasFragment ||
          uri.port < 1 ||
          uri.port > 65535 ||
          (uri.path.isNotEmpty && uri.path != '/')) {
        return null;
      }
      return uri.origin;
    } on FormatException {
      return null;
    }
  }
}
