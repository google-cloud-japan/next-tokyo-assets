import 'package:flutter/widgets.dart';

extension SafeContextExtension on State {
  /// `mounted` が true の場合のみ実行する汎用メソッド
  void safeUseContext(void Function(BuildContext context) action) {
    if (mounted) {
      action(context);
    }
  }
}
