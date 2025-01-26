// lib/viewmodel/auth_viewmodel.dart
import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../model/user_credentials.dart';
import '../view/common/snackbar_helper.dart';

final authViewModelProvider = ChangeNotifierProvider((ref) => AuthViewModel());

class AuthViewModel extends ChangeNotifier {
  final FirebaseAuth _firebaseAuth = FirebaseAuth.instance;

  Future<void> signUp(UserCredentials credentials, BuildContext context) async {
    if (!credentials.isValid) {
      SnackbarHelper.show(context, 'メールアドレスとパスワードを入力してください。');
      return;
    }

    try {
      await _firebaseAuth.createUserWithEmailAndPassword(
        email: credentials.email,
        password: credentials.password,
      );
      SnackbarHelper.show(context, 'ユーザー登録に成功しました');
      Navigator.pushReplacementNamed(context, '/chat');
    } on FirebaseAuthException catch (e) {
      SnackbarHelper.show(context, '登録エラー: ${e.message}');
    }
  }

  Future<void> signIn(UserCredentials credentials, BuildContext context) async {
    if (!credentials.isValid) {
      SnackbarHelper.show(context, 'メールアドレスとパスワードを入力してください。');
      return;
    }

    try {
      await _firebaseAuth.signInWithEmailAndPassword(
        email: credentials.email,
        password: credentials.password,
      );
      SnackbarHelper.show(context, 'ログインに成功しました');
      if (context.mounted) {
        Navigator.pushReplacementNamed(context, '/chat');
      }
    } on FirebaseAuthException catch (e) {
      SnackbarHelper.show(context, 'ログインエラー: ${e.message}');
    }
  }
}
