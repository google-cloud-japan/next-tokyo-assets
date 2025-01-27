// lib/view/sign_in_screen.dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../viewmodel/auth_viewmodel.dart';
import '../model/user_credentials.dart';

class SignInScreen extends ConsumerWidget {
  const SignInScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final authViewModel = ref.read(authViewModelProvider);
    final emailController = TextEditingController();
    final passwordController = TextEditingController();

    return Scaffold(
      appBar: AppBar(
        title: const Text('サインイン / サインアップ'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            TextField(
              controller: emailController,
              decoration: const InputDecoration(labelText: 'Email'),
            ),
            TextField(
              controller: passwordController,
              obscureText: true,
              decoration: const InputDecoration(labelText: 'Password'),
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: ElevatedButton(
                    onPressed: () {
                      final credentials = UserCredentials(
                        email: emailController.text.trim(),
                        password: passwordController.text.trim(),
                      );
                      authViewModel.signUp(credentials, context);
                    },
                    child: const Text('Sign Up'),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: ElevatedButton(
                    onPressed: () {
                      final credentials = UserCredentials(
                        email: emailController.text.trim(),
                        password: passwordController.text.trim(),
                      );
                      authViewModel.signIn(credentials, context);
                    },
                    child: const Text('Sign In'),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            // --- 【追加】Googleでサインイン ボタン ---
            ElevatedButton(
              onPressed: () async {
                // Googleサインイン処理を呼び出す
                // authViewModel.googleSignIn(context);
                await ref.read(authViewModelProvider).signInWithGoogle();
                Navigator.pushReplacementNamed(context, '/chat');
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.white,
                foregroundColor: Colors.black,
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Image.asset(
                    'assets/images/google_logo.png', // もしGoogleロゴ画像を置くなら
                    height: 24,
                  ),
                  const SizedBox(width: 8),
                  const Text('Sign in with Google'),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
