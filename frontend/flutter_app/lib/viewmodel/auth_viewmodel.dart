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

  Future<void> googleSignIn(BuildContext context) async {
    try {
      // サインイン済みなら signInSilently を試行
      final existingUser = await _googleSignIn.signInSilently();
      if (existingUser != null) {
        // すでにログイン済みなら、そのまま使う
        print("Already signed in with Google: ${existingUser.email}");
        // ここでトークンを取得し、バックエンド連携するなり Firebase Auth にリンクするなり
        final auth = await existingUser.authentication;
        final accessToken = auth.accessToken;
        final idToken = auth.idToken;
        print('AccessToken: $accessToken');
        print('IDToken: $idToken');
        // TODO: サーバーへ送信 or Firebase signInWithCredential など
        Navigator.pushReplacementNamed(context, '/chat');
        return;
      }

      // まだなら、Googleアカウント選択画面が出る
      final account = await _googleSignIn.signIn();
      if (account == null) {
        // ユーザーがキャンセルした
        print("Google sign in cancelled by user.");
        return;
      }

      // 成功時の処理
      print("Google sign in success: ${account.email}");
      final auth = await account.authentication;
      final accessToken = auth.accessToken;
      final idToken = auth.idToken;
      print('AccessToken: $accessToken');
      print('IDToken: $idToken');
      Navigator.pushReplacementNamed(context, '/chat');

      // TODO: ここでサーバーにトークンを渡す or Firebaseと連携など
      // 例: Firebaseに連携する場合 => signInWithCredential(GoogleAuthProvider.credential(idToken: idToken))
      // 例: 独自バックエンドの場合 => POST /google_auth でサーバーサイド検証
    } catch (e) {
      print("Google sign in failed: $e");
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text("Google SignIn Failed: $e")),
      );
    }
  }

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
        print("AccessToken : ${googleAuth.accessToken}");
        // ここで FirebaseAuth にサインイン
        await FirebaseAuth.instance.signInWithCredential(credential);

        // これで FirebaseAuth.instance.currentUser が有効になる
        print("FirebaseAuth signIn success: ${FirebaseAuth.instance.currentUser?.uid}");
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
