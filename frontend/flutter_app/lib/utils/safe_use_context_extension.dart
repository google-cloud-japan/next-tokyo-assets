import 'package:flutter/material.dart';

void safeUseContext(
    BuildContext context, void Function(BuildContext) callback) {
  if (context.mounted) {
    callback(context);
  }
}
