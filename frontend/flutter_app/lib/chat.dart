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

  /// 新規目標をFirestoreに追加する
  Future<void> _addObjective(String objective) async {
    // 現在ログインしているユーザー
    final currentUser = FirebaseAuth.instance.currentUser;
    if (currentUser == null) {
      // ログインしていない場合のエラーハンドリング
      return;
    }

    try {
      final objectiveId = _firestore
          .collection('users')
          .doc(currentUser.uid)
          .collection('objectives')
          .doc()
          .id;
      await _firestore
          .collection('users')
          .doc(currentUser.uid)
          .collection('objectives')
          .doc(objectiveId)
          .set({
        'objective': objective,
        'createdAt': FieldValue.serverTimestamp(),
      });
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('目標が追加されました')),
      );
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
      backgroundColor: Colors.grey[200],
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
        backgroundColor: Colors.white,
        child: SafeArea(
          child: ListView(
            padding: EdgeInsets.zero,
            children: [
              SizedBox(
                height: 150,
                child: DrawerHeader(
                  decoration: BoxDecoration(
                    color: Colors.blue[800],
                  ),
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const Text(
                        '目標一覧',
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: 24,
                        ),
                      ),
                      Padding(
                        padding: const EdgeInsets.all(8.0),
                        child: ElevatedButton.icon(
                          onPressed: () {
                            showDialog(
                              context: context,
                              builder: (BuildContext context) {
                                final TextEditingController
                                    objectiveController =
                                    TextEditingController();
                                return AlertDialog(
                                  title: const Text('新規目標追加'),
                                  content: TextField(
                                    controller: objectiveController,
                                    decoration: const InputDecoration(
                                      hintText: '目標を入力してください',
                                    ),
                                  ),
                                  actions: [
                                    TextButton(
                                      onPressed: () {
                                        Navigator.of(context).pop();
                                      },
                                      child: const Text('キャンセル'),
                                    ),
                                    TextButton(
                                      onPressed: () {
                                        final objective =
                                            objectiveController.text.trim();
                                        if (objective.isNotEmpty) {
                                          _addObjective(objective);
                                        }
                                        Navigator.of(context).pop();
                                      },
                                      child: const Text('追加'),
                                    ),
                                  ],
                                );
                              },
                            );
                          },
                          icon: const Icon(Icons.add),
                          label: const Text('新規目標'),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              StreamBuilder<QuerySnapshot>(
                stream: _firestore
                    .collection('users')
                    .doc(currentUser.uid)
                    .collection('objectives')
                    .orderBy('createdAt', descending: true)
                    .snapshots(),
                builder: (context, snapshot) {
                  if (!snapshot.hasData) {
                    return const Center(child: CircularProgressIndicator());
                  }
                  final docs = snapshot.data!.docs;
                  return ListView.builder(
                    shrinkWrap: true,
                    itemCount: docs.length,
                    itemBuilder: (context, index) {
                      final data = docs[index].data() as Map<String, dynamic>;
                      final objective = data['objective'] ?? 'No Objective';
                      return ListTile(
                        title: Text(objective),
                        onTap: () {
                          Navigator.pop(context);
                          // 目標をタップしたときの処理をここに記述
                          // そのObjectiveのIDを取得して、それに紐づくchatを表示する
                        },
                      );
                    },
                  );
                },
              ),
            ],
          ),
        ),
      ),
      body: SafeArea(
        child: Column(
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
              padding:
                  const EdgeInsets.only(right: 16.0, left: 16.0, bottom: 32.0),
              child: Row(
                children: [
                  Expanded(
                    child: Container(
                      height: 60, // 高さを広く設定
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(12), // 角を丸くする
                        border: Border.all(color: Colors.grey), // 枠線を追加
                      ),
                      child: TextField(
                        controller: _textController,
                        decoration: const InputDecoration(
                          hintText: 'Enter message',
                          border: InputBorder.none, // デフォルトの枠線を削除
                          contentPadding: EdgeInsets.symmetric(
                              horizontal: 16, vertical: 16), // 内側の余白を設定
                        ),
                      ),
                    ),
                  ),
                  IconButton(
                    icon: const Icon(
                      Icons.send,
                      color: Colors.blueAccent,
                    ),
                    onPressed: _addMessage,
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
