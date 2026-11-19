"""iOS 빌드 가드(ios/Flutter/verify_native_environment.py)와 네이티브 설정 파일의 짝을 검사한다."""
import base64
import importlib.util
from pathlib import Path
import plistlib
import unittest

ROOT = Path(__file__).resolve().parents[2]


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


ios = module('ios', 'ios/Flutter/verify_native_environment.py')

PROD = {'CLIENT_APP_ENV': 'prod', 'CLIENT_INVITE_LINK_ORIGIN': 'https://invite.example.com',
        'CLIENT_KAKAO_NATIVE_APP_KEY': 'abc123'}


def encoded(defines):
    return ','.join(base64.b64encode(f'{k}={v}'.encode()).decode() for k, v in defines.items())


def native(defines):
    settings = dict(line.split(' = ', 1) for line in ios.xcconfig(defines).splitlines()
                    if ' = ' in line)
    settings['PRODUCT_BUNDLE_IDENTIFIER'] = settings['CLIENT_APPLICATION_ID']
    settings['DART_DEFINES'] = encoded(defines)
    return settings


class MobileEnvironmentTest(unittest.TestCase):
    def test_native_identity_is_distinct_and_cannot_be_overridden(self):
        for environment in ('test', 'prod'):
            identity = ios.native_identity(environment)
            defines = {**(PROD if environment == 'prod' else {}), 'CLIENT_APP_ENV': environment}
            ios.expected_settings({**defines, **identity})
            for key in identity:
                with self.assertRaises(ValueError):
                    ios.expected_settings({**defines, key: 'other-environment'})
        for key in ios.native_identity('test'):
            self.assertNotEqual(ios.native_identity('test')[key], ios.native_identity('prod')[key])
        with self.assertRaises(ValueError):
            ios.native_identity('staging')

    def test_xcode_gate_rejects_stale_native_config_for_every_identity_field(self):
        settings = native(PROD)
        ios.verify(settings)
        for key in ('CLIENT_APP_ENV', 'CLIENT_APPLICATION_ID', 'PRODUCT_BUNDLE_IDENTIFIER',
                    'CLIENT_INVITE_SCHEME', 'CLIENT_KAKAO_NATIVE_KEY', 'CLIENT_INVITE_HOST'):
            with self.subTest(key=key), self.assertRaises(ValueError):
                ios.verify({**settings, key: 'stale-test-value'})
        with self.assertRaises(ValueError):
            ios.verify({**settings, 'DART_DEFINES': 'malformed'})

    def test_invite_origin_must_be_a_default_port_https_dns_origin(self):
        self.assertEqual(ios.invite_host('https://Invite.Example.com/'), 'invite.example.com')
        # 주지 않으면 앱 링크 도메인은 예약 도메인이다(앱 전용 스킴만 쓴다).
        self.assertEqual(ios.invite_host(''), ios.UNSET_INVITE_HOST)
        self.assertTrue(ios.UNSET_INVITE_HOST.endswith('.invalid'))
        for origin in ('http://invite.example.com', 'https://invite.example.com:8443',
                       'https://invite.example.com/path', 'https://user@invite.example.com',
                       'https://127.0.0.1', 'https://localhost'):
            with self.subTest(origin=origin), self.assertRaises(ValueError):
                ios.invite_host(origin)

    def test_kakao_key_format_is_checked(self):
        with self.assertRaises(ValueError):
            ios.expected_settings({**PROD, 'CLIENT_KAKAO_NATIVE_APP_KEY': 'not a key'})

    def test_print_xcconfig_covers_every_build_setting_the_gate_reads(self):
        text = ios.xcconfig(PROD)
        for key in ('CLIENT_APP_ENV', 'CLIENT_APPLICATION_ID', 'CLIENT_INVITE_SCHEME',
                    'CLIENT_KAKAO_NATIVE_KEY', 'CLIENT_INVITE_HOST', 'CLIENT_DISPLAY_NAME'):
            self.assertIn(f'{key} = ', text)
        self.assertEqual(ios.main(['--print-xcconfig', 'CLIENT_APP_ENV=staging']), 1)

    def test_native_sources_consume_generated_identity(self):
        manifest = (ROOT / 'android/app/src/main/AndroidManifest.xml').read_text()
        self.assertIn('android:scheme="${inviteScheme}"', manifest)
        self.assertIn('android:scheme="kakao${kakaoNativeAppKey}"', manifest)
        info = plistlib.loads((ROOT / 'ios/Runner/Info.plist').read_bytes())
        self.assertEqual([entry['CFBundleURLSchemes'][0] for entry in info['CFBundleURLTypes']],
                         ['kakao$(CLIENT_KAKAO_NATIVE_KEY)', '$(CLIENT_INVITE_SCHEME)'])
        # 카카오톡 설치 확인은 미리 밝힌 스킴만 조회할 수 있다.
        self.assertIn('kakaokompassauth', info['LSApplicationQueriesSchemes'])
        entitlements = plistlib.loads((ROOT / 'ios/Runner/Runner.entitlements').read_bytes())
        self.assertEqual(entitlements['com.apple.developer.associated-domains'],
                         ['applinks:$(CLIENT_INVITE_HOST)'])
        self.assertIn('verify_native_environment.py', (ROOT / 'ios/Runner.xcodeproj/project.pbxproj').read_text())

    def test_local_defaults_pass_the_gate(self):
        defaults = {}
        for line in (ROOT / 'ios/Flutter/EnvironmentDefaults.xcconfig').read_text().splitlines():
            if '=' in line and not line.lstrip().startswith('//'):
                key, value = line.split('=', 1)
                defaults[key.strip()] = value.strip()
        defaults['PRODUCT_BUNDLE_IDENTIFIER'] = defaults['CLIENT_APPLICATION_ID']
        defaults['DART_DEFINES'] = ''
        ios.verify(defaults)


if __name__ == '__main__':
    unittest.main()
