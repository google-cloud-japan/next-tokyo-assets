import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter/material.dart';

final firebaseAuthProvider = Provider<FirebaseAuthService>((ref) {
  return FirebaseAuthService(FirebaseAuth.instance);
});

class FirebaseAuthService {
  final FirebaseAuth _auth;

  FirebaseAuthService(this._auth);

  Future<void> signUp(String email, String password) async {
    try {
      UserCredential userCredential =
          await _auth.createUserWithEmailAndPassword(
        email: email,
        password: password,
      );
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
    try {
      await _auth.signOut();
      debugPrint('User signed out');
    } catch (e) {
      debugPrint('Sign out failed: $e');
    }
  }
}
