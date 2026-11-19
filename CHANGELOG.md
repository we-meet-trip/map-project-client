# 변경 기록

이 문서는 [Keep a Changelog](https://keepachangelog.com/ko/1.1.0/) 형식을 따르고, 버전은 [유의적 버전](https://semver.org/lang/ko/)을 따른다. 공개본에는 날짜를 기록하지 않는다.

## [1.0.0]

첫 공개본이다.

### 추가
- 공개 표준 파일(LICENSE·AUTHORS·CONTRIBUTING·CODE_OF_CONDUCT·SECURITY·CHANGELOG), 이슈·PR 템플릿.
- 문서: README, `docs/architecture.md`·`docs/data.md`·`docs/contracts.md`·`docs/troubleshooting.md`·`docs/decisions/`, 다이어그램과 근거표(`docs/diagrams/`).
- `scripts/fetch_fonts.sh`: 앱 글꼴(Pretendard, OFL)을 배포처에서 받아 sha256 을 확인한다.
- `scripts/build_geo.py` 와 OpenStreetMap 행정경계 자료(`assets/geo/`, ODbL)·지도 위 출처 표시.
- iOS 빌드 가드의 `--print-xcconfig`(다른 환경용 xcconfig 생성), 루트 `.gitleaks.toml`.
- 시험: 행정경계 자료와 지역 목록의 약속, 초대 앱 전용 주소, 시트를 여는 것만으로는 사진을 청하지 않음.

### 변경
- Dart 패키지 이름 `map_project_client`, 번들 ID `map.project.client`(시험판 `.dev`), URL 스킴 `mapproject`(시험판 `-dev`).
- 앱 빌드값(dart-define·iOS 빌드 설정) 이름을 `CLIENT_` 접두로 바꿨다(`.env.example`).
- 운영 서버·호스팅·계정을 가리키던 기본값을 모두 비웠다. 값을 주지 않으면 로컬 서버를 보고, https 초대 링크·약관 메뉴·문의 메일은 꺼진다.
- 장소 사진은 '사진 보기'를 누를 때만 불러온다. 기본 화면에는 원본 지도 링크만 둔다.
- 앱 글꼴은 저장소에 두지 않고 빌드 때 받는다. 로그인·블로그 표지는 직접 그린 중립 아이콘으로 바꿨다.
- 앱 버전을 1.0.0 으로 정리했다.

### 삭제
- 설치본 서명·스토어 제출·호스팅 게시 워크플로와 그 도구·시험.
- 호스팅에 올리던 법률 문서·초대 안내 페이지·랜딩 페이지와 배포 설정.
- 날짜가 든 내부 검토·스토어 신고·릴리스 문서.
- 이용조건을 확인하지 못한 행정경계 파일, 제3자 로고·배지.
- 화면이 쓰지 않는 코드(지하철 경로 조회, 장소 탐색 목업, 비전 결과 카드).

### 수정
- 서버가 초대 주소를 주지 않을 때 초대 공유 창이 빈 값을 보이고 복사하던 문제.
- 정책 문서 사이트가 없는 빌드에서 마이페이지 약관 메뉴를 누르면 오류가 나던 문제.

### 비공개 개발본과 달라진 점
- 운영 환경 전용 배포·백업·전환 도구와 운영 설정을 뺐다. 공개본은 로컬에서 직접 준비한 설정으로 실행한다.
- 공개본의 이름(저장소·패키지·이미지)은 비공개 개발본과 다르다. 비공개 운영 자료(스냅숏·설정·이미지)와 호환되지 않는다.

### 히스토리 정리 안내
- 공개 전에 커밋 히스토리를 정리했다. 실제 데이터·내부 문서·민감 정보를 히스토리에서 걷어냈고, 작성자 이메일을 GitHub noreply 주소로 통일했으며, 커밋 시각은 순서만 남긴 임의 값으로 바꿨다.
- 커밋 메시지 속 옛 이름은 현재 이름이나 중립 표현으로 바꿨다. 그래서 과거 커밋의 코드와 메시지 속 이름이 서로 다를 수 있다.

[1.0.0]: https://github.com/we-meet-trip/map-project-client/releases/tag/v1.0.0
