import 'package:firebase_auth/firebase_auth.dart';

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
      print('User signed up: ${user.uid}');
    }
  } on FirebaseAuthException catch (e) {
    print('Sign up failed: $e');
  } catch (e) {
    print(e.toString());
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
      print('User signed in: ${user.uid}');
    }
  } on FirebaseAuthException catch (e) {
    print('Sign in failed: $e');
  } catch (e) {
    print(e.toString());
  }
}

Future<void> signOut() async {
  await _auth.signOut();
  print('User signed out');
}

