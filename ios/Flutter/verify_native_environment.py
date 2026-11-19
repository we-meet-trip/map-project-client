#!/usr/bin/env python3
"""Xcode 빌드 단계에서 Dart 빌드값과 네이티브 번들·링크 설정이 어긋나면 빌드를 멈춘다.

앱의 번들 ID·초대 스킴·카카오 복귀 스킴·초대 링크 도메인은 두 곳에서 정해진다.
Dart 쪽은 `--dart-define` 으로 받은 값이고, 네이티브 쪽은 xcconfig 의 빌드 설정이다.
둘이 어긋난 채로 빌드되면 앱은 뜨지만 로그인 복귀나 초대 링크만 조용히 실패한다.
그래서 매 빌드마다 두 값을 대조한다.

다른 환경(prod 등)으로 빌드할 때는 `--print-xcconfig` 로 맞는 설정을 만들어
`ios/Flutter/NativeEnvironment.xcconfig`(git 에서 제외됨)에 저장한다.
    python3 ios/Flutter/verify_native_environment.py --print-xcconfig \
        CLIENT_APP_ENV=prod CLIENT_INVITE_LINK_ORIGIN=https://example.com CLIENT_KAKAO_NATIVE_APP_KEY=...
"""
import base64
import ipaddress
import os
import re
import sys
from urllib.parse import urlsplit

ENVIRONMENTS = ('test', 'prod')
# CLIENT_INVITE_LINK_ORIGIN 을 주지 않은 빌드의 앱 링크 도메인. 결코 존재하지 않는 예약
# 도메인(.invalid)이라 도메인 검증이 일어나지 않고, 초대는 앱 전용 스킴으로만 열린다.
# Android 빌드 파일(android/app/build.gradle.kts)과 같은 값이다.
UNSET_INVITE_HOST = 'invite.example.invalid'


def native_identity(environment):
    """환경마다 고정된 네이티브 신원. 빌드값으로 덮어쓸 수 없다."""
    if environment not in ENVIRONMENTS:
        raise ValueError('CLIENT_APP_ENV must be test or prod')
    suffix = '.dev' if environment == 'test' else ''
    scheme_suffix = '-dev' if environment == 'test' else ''
    return {
        'CLIENT_NATIVE_APPLICATION_ID': 'map.project.client' + suffix,
        'CLIENT_INVITE_URL_SCHEME': 'mapproject' + scheme_suffix,
    }


def decode_defines(raw):
    """Flutter 가 Xcode 에 넘기는 DART_DEFINES(쉼표로 이은 base64 목록)를 푼다."""
    defines = {}
    try:
        for item in raw.split(','):
            if item:
                name, value = base64.b64decode(item, validate=True).decode().split('=', 1)
                if name in defines:
                    raise ValueError('duplicate define')
                defines[name] = value
    except (ValueError, UnicodeError):
        raise ValueError('Malformed DART_DEFINES') from None
    return defines


def invite_host(origin):
    """초대 링크 origin 에서 앱 링크 도메인을 뽑는다. 기본 포트의 https DNS 이름만 받는다."""
    origin = origin.strip()
    if not origin:
        return UNSET_INVITE_HOST
    try:
        uri = urlsplit(origin)
        port = uri.port
    except ValueError:
        raise ValueError('CLIENT_INVITE_LINK_ORIGIN: malformed URL') from None
    host = (uri.hostname or '').lower()
    if (uri.scheme != 'https' or not host or uri.username is not None or uri.password is not None
            or uri.query or uri.fragment or uri.path not in ('', '/') or port not in (None, 443)):
        raise ValueError('CLIENT_INVITE_LINK_ORIGIN: an https origin on the default port is required')
    try:
        ipaddress.ip_address(host)
    except ValueError:
        pass
    else:
        raise ValueError('CLIENT_INVITE_LINK_ORIGIN: native links require a DNS hostname')
    if '.' not in host or not all(re.fullmatch(r'[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?', label)
                                  for label in host.split('.')):
        raise ValueError('CLIENT_INVITE_LINK_ORIGIN: native links require a DNS hostname')
    return host


def expected_settings(defines):
    """Dart 빌드값에서 Xcode 빌드 설정이 가져야 할 값을 만든다."""
    environment = defines.get('CLIENT_APP_ENV', 'test')
    identity = native_identity(environment)
    for field, value in identity.items():
        if field in defines and defines[field] != value:
            raise ValueError(f'{field} disagrees with CLIENT_APP_ENV')
    kakao_key = defines.get('CLIENT_KAKAO_NATIVE_APP_KEY', '').strip()
    if kakao_key and not re.fullmatch(r'[A-Za-z0-9]+', kakao_key):
        raise ValueError('CLIENT_KAKAO_NATIVE_APP_KEY: invalid client key format')
    return {
        'CLIENT_APP_ENV': environment,
        'CLIENT_APPLICATION_ID': identity['CLIENT_NATIVE_APPLICATION_ID'],
        'PRODUCT_BUNDLE_IDENTIFIER': identity['CLIENT_NATIVE_APPLICATION_ID'],
        'CLIENT_INVITE_SCHEME': identity['CLIENT_INVITE_URL_SCHEME'],
        'CLIENT_KAKAO_NATIVE_KEY': kakao_key,
        'CLIENT_INVITE_HOST': invite_host(defines.get('CLIENT_INVITE_LINK_ORIGIN', '')),
    }


def xcconfig(defines):
    """NativeEnvironment.xcconfig 내용. PRODUCT_BUNDLE_IDENTIFIER 는 프로젝트가 CLIENT_APPLICATION_ID 에서 읽는다."""
    values = {k: v for k, v in expected_settings(defines).items() if k != 'PRODUCT_BUNDLE_IDENTIFIER'}
    values['CLIENT_DISPLAY_NAME'] = 'MAP Dev' if values['CLIENT_APP_ENV'] == 'test' else 'MAP'
    return '// verify_native_environment.py --print-xcconfig 로 만든 파일. 직접 고치지 않는다.\n' + ''.join(
        f'{key} = {value}\n' for key, value in values.items())


def verify(environ):
    defines = decode_defines(environ.get('DART_DEFINES', ''))
    for field, value in expected_settings(defines).items():
        if environ.get(field) != value:
            raise ValueError(f'{field} disagrees with Dart config; regenerate NativeEnvironment.xcconfig')


def main(argv):
    if argv[:1] == ['--print-xcconfig']:
        try:
            pairs = dict(arg.split('=', 1) for arg in argv[1:])
            sys.stdout.write(xcconfig(pairs))
        except ValueError as error:
            print(f'error: {error}', file=sys.stderr)
            return 1
        return 0
    try:
        verify(os.environ)
    except ValueError as error:
        print(f'error: native environment rejected: {error}', file=sys.stderr)
        return 1
    print('Native bundle ID, callback, invite host and Dart environment agree')
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
