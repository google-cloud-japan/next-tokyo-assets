import 'package:flutter/material.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:hackathon_test1/chat.dart';
import 'package:hackathon_test1/utils/safe_use_context_extension.dart';
import 'firebase_options.dart';
import 'package:firebase_auth/firebase_auth.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  // Firebase初期化
  await Firebase.initializeApp(
    options: DefaultFirebaseOptions.currentPlatform,
  );
  runApp(const MyApp());
}

/// アプリ全体のルートWidget
class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Firebase Demo',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        elevatedButtonTheme: ElevatedButtonThemeData(
          style: ElevatedButton.styleFrom(
            backgroundColor: Colors.blue,
            foregroundColor: Colors.white,
          ),
        ),
      ),
      initialRoute: '/',
      routes: {
        '/': (context) => const AuthGate(),
        '/chat': (context) => const ChatPage(),
      },
    );
  }
}

/// FirebaseAuth のログイン状態によって画面を切り替えるウィジェット
class AuthGate extends StatelessWidget {
  const AuthGate({super.key});

  @override
  Widget build(BuildContext context) {
    // authStateChanges()を監視し、ユーザーがログインしているかを判定
    return StreamBuilder<User?>(
      stream: FirebaseAuth.instance.authStateChanges(),
      builder: (context, snapshot) {
        // ログイン判定中
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Scaffold(
            body: Center(child: CircularProgressIndicator()),
          );
        }
        // ログインしていない場合 → ログイン画面へ
        if (!snapshot.hasData) {
          return const SignInScreen();
        }
        // ログイン済みの場合 → メイン画面へ
        WidgetsBinding.instance.addPostFrameCallback((_) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('ログインしました : ${snapshot.data!.email}')),
          );
        });
        return const ChatPage();
      },
    );
  }
}

/// ユーザーがログインしていない時に表示するサインイン画面
class SignInScreen extends StatefulWidget {
  const SignInScreen({super.key});

  @override
  State<SignInScreen> createState() => _SignInScreenState();
}

class _SignInScreenState extends State<SignInScreen> {
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();

  /// 新規登録処理
  Future<void> _signUp() async {
    final email = _emailController.text.trim();
    final password = _passwordController.text.trim();

    if (!mounted) {
      throw Exception('Widget is no longer mounted.');
    }

    try {
      UserCredential userCredential =
          await FirebaseAuth.instance.createUserWithEmailAndPassword(
        email: email,
        password: password,
      );
      User? user = userCredential.user;
      safeUseContext((context) {
        if (user != null) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('ユーザー登録に成功しました')),
          );
          Navigator.pushReplacementNamed(context, '/chat');
        }
      });
    } on FirebaseAuthException catch (e) {
      safeUseContext((context) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('登録エラー: ${e.message}')),
        );
      });
    } catch (e) {
      safeUseContext((context) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('エラー: $e')),
        );
      });
    }
  }

  /// ログイン処理
  Future<void> _signIn() async {
    final email = _emailController.text.trim();
    final password = _passwordController.text.trim();
    try {
      await FirebaseAuth.instance.signInWithEmailAndPassword(
        email: email,
        password: password,
      );
      safeUseContext((context) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('ログインに成功しました')),
        );
      });
    } on FirebaseAuthException catch (e) {
      safeUseContext((context) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('ログインエラー: ${e.message}')),
        );
      });
    } catch (e) {
      safeUseContext((context) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('エラー: $e')),
        );
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('サインイン / サインアップ'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            TextField(
              controller: _emailController,
              decoration: const InputDecoration(labelText: 'Email'),
            ),
            TextField(
              controller: _passwordController,
              obscureText: true,
              decoration: const InputDecoration(labelText: 'Password'),
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: ElevatedButton(
                    onPressed: _signUp,
                    child: const Text('Sign Up'),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: ElevatedButton(
                    onPressed: _signIn,
                    child: const Text('Sign In'),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
