import 'package:flutter/material.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:cloud_firestore/cloud_firestore.dart';

/// ユーザーがログイン済みのときに表示するホーム画面
class ChatPage extends StatefulWidget {
  const ChatPage({super.key});

  @override
  State<ChatPage> createState() => _ChatPageState();
}

class _ChatPageState extends State<ChatPage> {
  final _firestore = FirebaseFirestore.instance;
  final _textController = TextEditingController();
  final notebookId = 'tekitotekito'; // 画面遷移時に受け取るなど

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
        title: const Text('Chat'),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: _signOut,
          )
        ],
      ),
      drawer: Drawer(
        child: ListView(
          padding: EdgeInsets.zero,
          children: [
            const DrawerHeader(
              decoration: BoxDecoration(
                color: Colors.blue,
              ),
              child: Text(
                'Chat History',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 24,
                ),
              ),
            ),
            ListTile(
              title: const Text('Chat 1'),
              onTap: () {
                Navigator.pop(context);
                // ダミーデータのチャット履歴を表示
              },
            ),
            ListTile(
              title: const Text('Chat 2'),
              onTap: () {
                Navigator.pop(context);
                // ダミーデータのチャット履歴を表示
              },
            ),
            ListTile(
              title: const Text('Chat 3'),
              onTap: () {
                Navigator.pop(context);
                // ダミーデータのチャット履歴を表示
              },
            ),
          ],
        ),
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
                    final createdAt =
                        data['createdAt']?.toDate().toString() ?? 'No Time';

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
                    decoration:
                        const InputDecoration(hintText: 'Enter message'),
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
