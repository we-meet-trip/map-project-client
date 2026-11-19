import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:map_project_client/features/chat/chat_limits.dart';
import 'package:map_project_client/features/chat/widgets/chat_input_bar.dart';

/// 서버가 거절할 길이의 메시지는 입력창에서부터 받지 않는다(서비스 사이 길이 약속은
/// 보내는 쪽이 지킨다). 서버 한도와 같은 값이어야 한다.
void main() {
  test('limit matches the server contract', () {
    expect(kChatMessageMaxLength, 2000);
  });

  testWidgets('input stops at the server limit', (tester) async {
    String? sent;
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(body: ChatInputBar(onSend: (text) => sent = text)),
      ),
    );
    await tester.enterText(
      find.byType(TextField),
      'a' * (kChatMessageMaxLength + 50),
    );
    await tester.pump();

    final field = tester.widget<TextField>(find.byType(TextField));
    expect(field.controller!.text.length, kChatMessageMaxLength);

    await tester.testTextInput.receiveAction(TextInputAction.done);
    await tester.pump();
    expect(sent?.length, kChatMessageMaxLength);
  });
}
