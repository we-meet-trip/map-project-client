#!/bin/sh
# 앱 글꼴 Pretendard(SIL Open Font License 1.1)를 받아 assets/fonts/ 에 둔다.
#
# 글꼴 파일은 6.7MB 라 저장소에 넣지 않는다. pubspec.yaml 이 이 자리의 파일을
# 선언하므로 `flutter pub get`·`flutter test`·빌드보다 먼저 한 번 실행한다.
# 받은 파일은 아래 sha256 과 맞아야 쓴다 — 배포처 파일이 바뀌면 여기서 멈춘다.
# 원본을 그대로 쓰므로 글꼴 이름(예약 이름 Pretendard)을 바꾸지 않는다. 라이선스
# 원문도 같이 받아 앱 자산에 함께 싣는다.
#
# 쓰임: sh scripts/fetch_fonts.sh   (이미 맞는 파일이 있으면 받지 않는다)
set -eu

cd "$(dirname "$0")/.."
DEST=assets/fonts
TAG=v1.3.9
GH="https://github.com/orioncactus/pretendard/raw/$TAG"
CDN="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@$TAG"

FONT_PATH=packages/pretendard/dist/public/variable/PretendardVariable.ttf
FONT_SHA256=3090ccde0442bb347aa7685d9ba8b17436a60682df6e8f92a9a670de14056e22
LICENSE_SHA256=d31ddd9f2bed32fd7e302a205cf2380ba0de6529152d239ef99cfb6f261bfc04

sha256() {
  if command -v sha256sum >/dev/null 2>&1; then
    sha256sum "$1" | cut -d' ' -f1
  else
    shasum -a 256 "$1" | cut -d' ' -f1
  fi
}

# fetch <저장할 파일> <기대 sha256> <주소>...
fetch() {
  out=$1 want=$2
  shift 2
  if [ -f "$out" ] && [ "$(sha256 "$out")" = "$want" ]; then
    echo "ok   $out"
    return 0
  fi
  for url in "$@"; do
    tmp="$out.part"
    if curl -fsSL --retry 2 --connect-timeout 20 -o "$tmp" "$url"; then
      if [ "$(sha256 "$tmp")" = "$want" ]; then
        mv "$tmp" "$out"
        echo "got  $out"
        return 0
      fi
      echo "warn $url: sha256 mismatch" >&2
    else
      echo "warn $url: download failed" >&2
    fi
    rm -f "$tmp"
  done
  echo "error: could not fetch $out" >&2
  return 1
}

mkdir -p "$DEST"
fetch "$DEST/PretendardVariable.ttf" "$FONT_SHA256" "$GH/$FONT_PATH" "$CDN/$FONT_PATH"
fetch "$DEST/OFL.txt" "$LICENSE_SHA256" "$GH/LICENSE" "$CDN/LICENSE"
