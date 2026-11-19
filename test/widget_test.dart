import 'package:flutter_test/flutter_test.dart';
import 'package:map_project_client/app.dart';

void main() {
  testWidgets('App smoke test', (WidgetTester tester) async {
    await tester.pumpWidget(const App());
  });
}
