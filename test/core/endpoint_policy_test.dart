import 'package:flutter_test/flutter_test.dart';
import 'package:map_project_client/core/config/endpoint_policy.dart';

const prod = EndpointPolicy(
  environment: 'prod',
  allowedOrigins: 'https://api.example.com',
  configUrl: 'https://config.example.com/prod.json',
  explicitOrigins: true,
);

void main() {
  test('production remote document must match the installed environment', () {
    expect(
      prod.remote({
        'environment': 'prod',
        'api_base_url': 'https://api.example.com/',
      }),
      'https://api.example.com',
    );
    for (final environment in [null, 'test', true, 'unknown']) {
      expect(
        prod.remote({
          'environment': environment,
          'api_base_url': 'https://api.example.com',
        }),
        isNull,
      );
    }
  });

  test(
    'all release sources obey the same exact canonical origin allowlist',
    () {
      expect(
        prod.trusted('https://API.EXAMPLE.COM:443/'),
        'https://api.example.com',
      );
      for (final url in [
        'http://api.example.com',
        'https://api.example.com:8443',
        'https://api.example.com/other',
        'https://api.example.com//',
        'https://api.example.com.evil.invalid',
        'https://api.example.com@evil.invalid',
        'https://api.example.com?token=x',
        'https://api.example.com#fragment',
        'https://api.example.com\\@evil.invalid',
        ' https://api.example.com',
        'https://api.example.com\n',
        'https://api.example.com:65536',
      ]) {
        expect(prod.trusted(url), isNull, reason: url);
        expect(
          prod.remote({'environment': 'prod', 'api_base_url': url}),
          isNull,
          reason: url,
        );
      }
    },
  );

  test('production must declare its own API origins', () {
    for (final policy in [
      const EndpointPolicy(
        environment: 'prod',
        allowedOrigins: 'https://api.example.com',
        configUrl: 'https://config.example.com/prod.json',
        explicitOrigins: false,
      ),
      const EndpointPolicy(
        environment: 'prod',
        allowedOrigins: '',
        configUrl: 'https://config.example.com/prod.json',
        explicitOrigins: true,
      ),
    ]) {
      expect(policy.valid, isFalse);
      expect(policy.trusted('https://api.example.com'), isNull);
    }
    // 원격 설정 주소는 선택이다.
    const noRemote = EndpointPolicy(
      environment: 'prod',
      allowedOrigins: 'https://api.example.com',
      configUrl: '',
      explicitOrigins: true,
    );
    expect(noRemote.valid, isTrue);
    expect(noRemote.hasRemoteConfig, isFalse);
    expect(
      noRemote.trusted('https://api.example.com'),
      'https://api.example.com',
    );
  });

  test('default test policy is valid but trusts no server', () {
    const policy = EndpointPolicy(
      environment: 'test',
      allowedOrigins: '',
      configUrl: '',
      explicitOrigins: false,
    );
    expect(policy.valid, isTrue);
    expect(policy.hasRemoteConfig, isFalse);
    expect(policy.trusted('https://api.example.test'), isNull);
    expect(
      policy.remote({
        'environment': 'test',
        'api_base_url': 'https://api.example.test',
      }),
      isNull,
    );
  });

  test('test policy trusts only the configured origins', () {
    const policy = EndpointPolicy(
      environment: 'test',
      allowedOrigins: 'https://api.example.test,https://api-alt.example.test',
      configUrl: 'https://config.example.test/app_config.json',
      explicitOrigins: true,
    );
    expect(policy.valid, isTrue);
    for (final origin in [
      'https://api.example.test',
      'https://api-alt.example.test',
    ]) {
      expect(
        policy.remote({'environment': 'test', 'api_base_url': '$origin/'}),
        origin,
      );
    }
    expect(
      policy.remote({
        'environment': 'test',
        'api_base_url': 'https://api.example.com',
      }),
      isNull,
    );
  });

  test('legacy test document is accepted only by the explicit test policy', () {
    const test = EndpointPolicy(
      environment: 'test',
      allowedOrigins: 'https://api-alt.example.test',
      configUrl: 'https://config.example.test/app_config.json',
      explicitOrigins: false,
    );
    expect(
      test.remote({'api_base_url': 'https://api-alt.example.test'}),
      'https://api-alt.example.test',
    );
    expect(
      test.remote({
        'environment': 'prod',
        'api_base_url': 'https://api-alt.example.test',
      }),
      isNull,
    );
  });

  test(
    'malformed configuration is rejected without throwing or making a request',
    () {
      for (final config in [
        'https://config.example.com:bad',
        'https://config.example.com:65536',
        'http://config.example.com',
        'https://user@config.example.com',
        'https://config.example.com?secret=1',
      ]) {
        final policy = EndpointPolicy(
          environment: 'prod',
          allowedOrigins: prod.allowedOrigins,
          configUrl: config,
          explicitOrigins: true,
        );
        expect(policy.valid, isFalse);
        expect(policy.trusted('https://api.example.com'), isNull);
      }
    },
  );
}
