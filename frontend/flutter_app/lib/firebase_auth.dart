import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/material.dart';

final FirebaseAuth _auth = FirebaseAuth.instance;

Future<void> signUp(String email, String password) async {
  try {
    UserCredential userCredential = await _auth.createUserWithEmailAndPassword(
      email: email,
      password: password,
    );
    // ユーザー情報取得
    User? user = userCredential.user;
    if (user != null) {
      debugPrint('User signed up: ${user.uid}');
    }
  } on FirebaseAuthException catch (e) {
    debugPrint('Sign up failed: $e');
  } catch (e) {
    debugPrint(e.toString());
  }
}

Future<void> signIn(String email, String password) async {
  try {
    UserCredential userCredential = await _auth.signInWithEmailAndPassword(
      email: email,
      password: password,
    );
    User? user = userCredential.user;
    if (user != null) {
      debugPrint('User signed in: ${user.uid}');
    }
  } on FirebaseAuthException catch (e) {
    debugPrint('Sign in failed: $e');
  } catch (e) {
    debugPrint(e.toString());
  }
}

Future<void> signOut() async {
  await _auth.signOut();
  debugPrint('User signed out');
}
