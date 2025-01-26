// lib/view/chat_page.dart
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:hackathon_test1/view/common/add_goal_button.dart';
import 'package:hackathon_test1/viewmodel/chat_viewmodel.dart';
import 'package:hackathon_test1/viewmodel/goal_viewmodel.dart';

class ChatPage extends ConsumerWidget {
  const ChatPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final viewModel = ref.watch(chatViewModelProvider);
    final goalViewModel = ref.watch(goalViewModelProvider);
    final user = FirebaseAuth.instance.currentUser;

    if (user == null) {
      return const Scaffold(
        body: Center(child: Text('ログインしていません')),
      );
    }

    final chatStream =
        viewModel.getChatStream(user.uid, viewModel.selectedGoalId);
    final goalStream = viewModel.getGoalStream(user.uid);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Chat'),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () async {
              await FirebaseAuth.instance.signOut();
            },
          ),
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
                        child: AddGoalButton(viewModel: goalViewModel),
                      ),
                    ],
                  ),
                ),
              ),
              StreamBuilder<QuerySnapshot>(
                stream: goalStream,
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
                      final goalId = docs[index].id; // 目標のIDを取得
                      return ListTile(
                        title: Text(goal),
                        onTap: () {
                          viewModel.setSelectedGoalId(goalId);
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
      body: Column(
        children: [
          // メッセージ一覧
          Expanded(
            child: viewModel.selectedGoalId != null
                ? StreamBuilder<QuerySnapshot>(
                    stream: chatStream,
                    builder: (context, snapshot) {
                      if (!snapshot.hasData) {
                        return const Center(child: CircularProgressIndicator());
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
                        AddGoalButton(viewModel: goalViewModel),
                      ],
                    ),
                  ),
          ),
          // 入力欄
          viewModel.selectedGoalId != null
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
                            controller: viewModel.textController,
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
                        onPressed: () {
                          viewModel.addMessage('tekitotekito', context);
                        },
                      ),
                    ],
                  ),
                )
              : const SizedBox(),
        ],
      ),
    );
  }
}
