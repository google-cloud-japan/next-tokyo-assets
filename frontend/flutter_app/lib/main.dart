import 'package:flutter/material.dart';
import 'package:firebase_core/firebase_core.dart';

// FlutterFire CLI で生成されたファイル（例：lib/firebase_options.dart）
import 'firebase_options.dart';

// Firebase Authentication
import 'package:firebase_auth/firebase_auth.dart';

// Firestore
import 'package:cloud_firestore/cloud_firestore.dart';

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
  const MyApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Firebase Demo',
      theme: ThemeData(primarySwatch: Colors.blue),
      home: const AuthGate(),
    );
  }
}

final notebookId = 'tekitotekito'; // 画面遷移時に受け取るなど


/// FirebaseAuth のログイン状態によって画面を切り替えるウィジェット
class AuthGate extends StatelessWidget {
  const AuthGate({Key? key}) : super(key: key);

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
        return const HomeScreen();
      },
    );
  }
}

/// ユーザーがログインしていない時に表示するサインイン画面
class SignInScreen extends StatefulWidget {
  const SignInScreen({Key? key}) : super(key: key);

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
    try {
      await FirebaseAuth.instance.createUserWithEmailAndPassword(
        email: email,
        password: password,
      );
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('ユーザー登録に成功しました')),
      );
    } on FirebaseAuthException catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('登録エラー: ${e.message}')),
      );
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
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('ログインに成功しました')),
      );
    } on FirebaseAuthException catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('ログインエラー: ${e.message}')),
      );
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

/// ユーザーがログイン済みのときに表示するホーム画面
class HomeScreen extends StatefulWidget {
  const HomeScreen({Key? key}) : super(key: key);

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final _firestore = FirebaseFirestore.instance;
  final _textController = TextEditingController();

  /// Firestoreにデータを追加する
  Future<void> _addMessage() async {
    final text = _textController.text.trim();
    if (text.isEmpty) return;

    // 現在ログインしているユーザー
    final currentUser = FirebaseAuth.instance.currentUser;
    if (currentUser == null) {
      // ログインしていない場合のエラーハンドリング
      return;
    }

    try {
      await _firestore
          .collection('users')
          .doc(currentUser.uid)
          .collection('notebooks')
          .doc(notebookId)
          .collection('chat')
          .add({
        'content': text,
        'createdAt': FieldValue.serverTimestamp(),
        'role': "user",
        'loading': false,
        'ragFileIds': null,
        'status': "success"
      });
      _textController.clear();
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Firestore書き込みエラー: $e')),
      );
    }
  }

  /// ログアウト処理
  Future<void> _signOut() async {
    await FirebaseAuth.instance.signOut();
  }

  @override
  Widget build(BuildContext context) {
    // ログインユーザーを取得
    final currentUser = FirebaseAuth.instance.currentUser;
    if (currentUser == null) {
      return const Scaffold(
        body: Center(child: Text('ログインしていません')),
      );
    }

    // ユーザーごとの messages サブコレクションをリアルタイム監視
    final messageStream = FirebaseFirestore.instance
        .collection('users')
        .doc(currentUser.uid)
        .collection('notebooks')
        .doc(notebookId)
        .collection('chat')
        .orderBy('createdAt', descending: true)
        .snapshots();

    return Scaffold(
      appBar: AppBar(
        title: const Text('Home'),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: _signOut,
          )
        ],
      ),
      body: Column(
        children: [
          // メッセージ一覧
          Expanded(
            child: StreamBuilder<QuerySnapshot>(
              stream: messageStream,
              builder: (context, snapshot) {
                if (!snapshot.hasData) {
                  return const Center(child: CircularProgressIndicator());
                }
                final docs = snapshot.data!.docs;
                return ListView.builder(
                  reverse: true,
                  itemCount: docs.length,
                  itemBuilder: (context, index) {
                    final data = docs[index].data() as Map<String, dynamic>;
                    final content = data['content'] ?? 'No Message';
                    final role = data['role'] ?? 'Unknown';
                    final createdAt = data['createdAt']?.toDate().toString() ?? 'No Time';

                    return ListTile(
                      title: Text(content),
                    );
                  },
                );
              },
            ),
          ),
          // 入力欄
          Padding(
            padding: const EdgeInsets.all(8.0),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _textController,
                    decoration: const InputDecoration(hintText: 'Enter message'),
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.send),
                  onPressed: _addMessage,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
