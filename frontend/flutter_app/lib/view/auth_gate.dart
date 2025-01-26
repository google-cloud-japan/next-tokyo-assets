import 'package:flutter/material.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'chat_page.dart';
import 'sign_in_screen.dart';
import 'common/snackbar_helper.dart';

class AuthGate extends StatelessWidget {
  const AuthGate({super.key});

  @override
  Widget build(BuildContext context) {
    return StreamBuilder<User?>(
      stream: FirebaseAuth.instance.authStateChanges(),
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Scaffold(
            body: Center(child: CircularProgressIndicator()),
          );
        }
        if (!snapshot.hasData) {
          return const SignInScreen();
        }
        WidgetsBinding.instance.addPostFrameCallback((_) {
          SnackbarHelper.show(context, 'ログインしました : ${snapshot.data!.email}');
        });
        return const ChatPage();
      },
    );
  }
}
