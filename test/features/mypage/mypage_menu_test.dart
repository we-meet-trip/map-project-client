import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:hive_flutter/hive_flutter.dart';
import 'package:map_project_client/data/local/profile_local_store.dart';
import 'package:map_project_client/features/mypage/screens/mypage_screen.dart';

/// 마이페이지 메뉴 구성을 고정한다.
///
/// 준비 중이던 알림 설정·공지/이벤트 자리는 없어졌다. 약관 및 정책과 고객센터는
/// 정책 사이트·문의 메일을 빌드값으로 줬을 때만 보인다 — 기본 빌드에는 없다.
/// 자리만 확인한다 — 눌렀을 때의 동작은 외부 앱을 열어 여기서 볼 수 없다.
void main() {
  setUpAll(() async {
    // 프로필 보관소가 값이 바뀔 때마다 기기에 적으므로 저장 공간이 있어야 한다.
    TestWidgetsFlutterBinding.ensureInitialized();
    final dir = await Directory.systemTemp.createTemp('map_mypage_menu_test');
    Hive.init(dir.path);
    await ProfileLocalStore.init();
  });

  testWidgets('기본 빌드에는 약관·고객센터가 없고 알림 설정·공지/이벤트도 없다', (tester) async {
    await tester.pumpWidget(
      const MaterialApp(home: Scaffold(body: MypageScreen())),
    );
    await tester.pump();

    expect(find.text('약관 및 정책'), findsNothing);
    expect(find.text('고객센터'), findsNothing);
    expect(find.text('외부 AI 전송 동의 설정'), findsOneWidget);
    await tester.tap(find.text('외부 AI 전송 동의 설정'));
    await tester.pumpAndSettle();
    expect(find.text('Vision 질문'), findsOneWidget);
    expect(find.text('여행 추천·재탐색'), findsOneWidget);
    expect(find.text('알림 설정'), findsNothing);
    expect(find.text('공지/이벤트'), findsNothing);
  });
}
