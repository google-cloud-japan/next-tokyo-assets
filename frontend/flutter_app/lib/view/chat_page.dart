// lib/view/chat_page.dart
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:hackathon_test1/view/common/add_goal_button.dart';
import 'package:hackathon_test1/viewmodel/chat_viewmodel.dart';
import 'package:hackathon_test1/viewmodel/goal_viewmodel.dart';

import 'first_input_widget.dart';

class ChatPage extends ConsumerWidget {
  const ChatPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final chatViewModel = ref.watch(chatViewModelProvider);
    final goalViewModel = ref.watch(goalViewModelProvider);
    final user = FirebaseAuth.instance.currentUser;

    if (user == null) {
      return const Scaffold(
        body: Center(child: Text('ログインしていません')),
      );
    }
    final userId = user.uid;

    final chatStream = chatViewModel.getChatStream(user.uid, chatViewModel.selectedGoalId);

    // 目標一覧のStream
    final goalStream = chatViewModel.getGoalStream(user.uid);
    // 現在選択中のgoalId
    final selectedGoalId = chatViewModel.selectedGoalId;

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
                          // 目標を選択する箇所
                          chatViewModel.setSelectedGoalId(goalId);
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
            child: chatViewModel.selectedGoalId != null
                ? StreamBuilder<QuerySnapshot>(
                    stream: chatStream,
                    builder: (context, snapshot) {
                      if (!snapshot.hasData) {
                        return const Center(child: CircularProgressIndicator());
                      }
                      final docs = snapshot.data!.docs;
                      final isEmpty = docs.isEmpty;
                      // チャットが空の場合は「期日」「週あたり作業時間」も入力できるフォームを下部に出す
                      if (isEmpty) {
                        return FirstInputWidget(
                          chatViewModel: chatViewModel,
                          userId: userId,
                          goalId: chatViewModel.selectedGoalId!,
                        );
                      } else {
                        // すでにチャットが存在する場合 -> 普通のメッセージ送信欄のみ
                        return SizedBox();
                      }
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
          // ★★入力欄
          StreamBuilder<QuerySnapshot>(
            stream: chatStream,
            builder: (context, snapshot) {
              // まだデータがない（ロード中）の場合は空表示にしておく
              if (!snapshot.hasData) {
                return const SizedBox();
              }

              // ドキュメントを取得
              final docs = snapshot.data!.docs;
              // チャットのドキュメントが空ではないか？
              final notEmpty = docs.isNotEmpty;
              // 目標が選択されているか？
              final hasGoalId = chatViewModel.selectedGoalId != null;

              // 両方の条件を満たす場合のみ入力欄を表示、それ以外は SizedBox() を返す
              if (hasGoalId && notEmpty) {
                return Padding(
                  padding: const EdgeInsets.only(right: 16.0, left: 16.0, bottom: 32.0),
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
                            controller: chatViewModel.textController,
                            decoration: const InputDecoration(
                              hintText: 'Enter message',
                              border: InputBorder.none,
                              contentPadding: EdgeInsets.symmetric(
                                horizontal: 16,
                                vertical: 16,
                              ),
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
                          chatViewModel.addMessage('tekitotekito', context);
                        },
                      ),
                    ],
                  ),
                );
              } else {
                return const SizedBox();
              }
            },
          ),
        ],
      ),
    );
  }
}
