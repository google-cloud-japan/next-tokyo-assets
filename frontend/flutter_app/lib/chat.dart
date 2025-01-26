import 'package:flutter/material.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:hackathon_test1/viewmodels/goal_viewmodel.dart';
import 'package:hackathon_test1/views/common/add_goal_button.dart';
import 'package:hackathon_test1/views/common/snackbar_helper.dart';

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
  String? selectedObjectiveId; // 選択された目標のIDを保持
  final GoalViewModel _objectiveViewModel = GoalViewModel();

  /// Firestoreにデータを追加する
  Future<void> _addMessage() async {
    final text = _textController.text.trim();
    if (text.isEmpty) return;

    // 現在ログインしているユーザー
    final currentUser = FirebaseAuth.instance.currentUser;
    if (currentUser == null) {
      SnackbarHelper.show(context, 'ログインしていません');
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
      // ignore: use_build_context_synchronously
      SnackbarHelper.show(context, 'メッセージが送信されました');
    } catch (e) {
      // ignore: use_build_context_synchronously
      SnackbarHelper.show(context, 'Firestore書き込みエラー: $e');
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

    // 選択された目標に基づいてチャットログを取得
    final chatStream = selectedObjectiveId != null
        ? _firestore
            .collection('users')
            .doc(currentUser.uid)
            .collection('objectives')
            .doc(selectedObjectiveId)
            .collection('chat')
            .orderBy('createdAt', descending: true)
            .snapshots()
        : null;

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
                        child: AddGoalButton(viewModel: _objectiveViewModel),
                      ),
                    ],
                  ),
                ),
              ),
              StreamBuilder<QuerySnapshot>(
                stream: _firestore
                    .collection('users')
                    .doc(currentUser.uid)
                    .collection('goals')
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
                      final goal = data['goal'] ?? 'No Goal';
                      final objectiveId = docs[index].id; // 目標のIDを取得
                      return ListTile(
                        title: Text(goal),
                        onTap: () {
                          setState(() {
                            selectedObjectiveId = objectiveId; // 選択された目標のIDをセット
                          });
                          Navigator.pop(context); // drawerを閉じる
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
              child: selectedObjectiveId != null
                  ? StreamBuilder<QuerySnapshot>(
                      stream: chatStream,
                      builder: (context, snapshot) {
                        if (!snapshot.hasData) {
                          return const Center(
                              child: CircularProgressIndicator());
                        }
                        final docs = snapshot.data!.docs;
                        return ListView.builder(
                          reverse: true,
                          itemCount: docs.length,
                          itemBuilder: (context, index) {
                            final data =
                                docs[index].data() as Map<String, dynamic>;
                            final content = data['content'] ?? 'No Message';
                            final role = data['role'] ?? 'Unknown';
                            final createdAt =
                                data['createdAt']?.toDate().toString() ??
                                    'No Time';

                            return ListTile(
                              title: Text(content),
                              subtitle: Text(createdAt),
                            );
                          },
                        );
                      },
                    )
                  : Center(
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          const Text('目標を選択してください'),
                          // TODO : chatStream が 存在する場合はドロワーを開くボタンを追加する
                          AddGoalButton(viewModel: _objectiveViewModel),
                        ],
                      ),
                    ),
            ),
            // 入力欄
            selectedObjectiveId != null
                ? Padding(
                    padding: const EdgeInsets.only(
                        right: 16.0, left: 16.0, bottom: 32.0),
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
                  )
                : const SizedBox(),
          ],
        ),
      ),
    );
  }
}
