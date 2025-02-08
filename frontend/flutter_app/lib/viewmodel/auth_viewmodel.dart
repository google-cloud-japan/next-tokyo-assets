// lib/viewmodel/auth_viewmodel.dart
import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_sign_in/google_sign_in.dart';
import '../model/user_credentials.dart';
import '../view/common/snackbar_helper.dart';
import 'package:flutter/foundation.dart' show kIsWeb;

final authViewModelProvider = ChangeNotifierProvider((ref) => AuthViewModel());

class AuthViewModel extends ChangeNotifier {
  final FirebaseAuth _firebaseAuth = FirebaseAuth.instance;
  /// ここでGoogleのアクセストークンを保持する
  String? _accessToken;
  /// アクセストークンを外部から参照できるようGetterを用意
  String? get accessToken => _accessToken;

  // 既存、メールアドレスとパスワードのサインアップ
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

  // 既存、メールアドレスとパスワードのサインイン
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
      print('ログインエラー: ${e.message}');
    }
  }
  // --- ここから Googleサインイン追加 ---
  final GoogleSignIn _googleSignIn = GoogleSignIn(
    scopes: [
      'email',
      'profile',
      'https://www.googleapis.com/auth/tasks',
    ],
  );

  // Googleサインアウト（必要であれば）
  Future<void> googleSignOut(BuildContext context) async {
    await _googleSignIn.signOut();
    print("Google signed out");
  }

  Future<void> signInWithGoogle() async {
    if (kIsWeb) {
      // Webの場合: signInWithPopup() が使える
      await FirebaseAuth.instance.signInWithPopup(GoogleAuthProvider());
    } else {
      // iOS/Androidの場合: google_sign_in を使う
      try {
        final googleUser = await _googleSignIn.signIn();
        if (googleUser == null) {
          // ユーザーがキャンセルした場合
          return;
        }
        final googleAuth = await googleUser.authentication;
        final credential = GoogleAuthProvider.credential(
          accessToken: googleAuth.accessToken,
          idToken: googleAuth.idToken,
        );
        _accessToken = googleAuth.accessToken;
        print("AccessToken : ${googleAuth.accessToken}");
        // ここで FirebaseAuth にサインイン
        await FirebaseAuth.instance.signInWithCredential(credential);
      } catch (e) {
        print("Google sign in error: $e");
      }
    }
  }

  Future<void> signInWithGooglePopup() async {
    // Web専用API: signInWithPopup
    await FirebaseAuth.instance.signInWithPopup(GoogleAuthProvider());

    // サインイン成功後は FirebaseAuth.instance.currentUser が取得できます
    final user = FirebaseAuth.instance.currentUser;
    print('User: ${user?.email}');
  }
}
