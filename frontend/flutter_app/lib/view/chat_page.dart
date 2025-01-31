import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:hackathon_test1/view/common/add_goal_button.dart';
import 'package:hackathon_test1/view/tasks_widget.dart';
import 'package:hackathon_test1/viewmodel/chat_viewmodel.dart';
import 'package:hackathon_test1/viewmodel/goal_viewmodel.dart';
import 'chat_input_widget.dart';
import 'first_input_widget.dart';

class ChatPage extends ConsumerWidget {
  const ChatPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // ViewModel の取得
    final chatViewModel = ref.watch(chatViewModelProvider);
    final goalViewModel = ref.watch(goalViewModelProvider);
    final user = FirebaseAuth.instance.currentUser;

    // ログインチェック
    if (user == null) {
      return const Scaffold(
        body: Center(child: Text('ログインしていません')),
      );
    }
    final userId = user.uid;

    // タブ表示全体を包む
    return DefaultTabController(
      length: 2, // タブ数
      child: Scaffold(
        appBar: AppBar(
          title: const Text('Task Trail'),
          actions: [
            IconButton(
              icon: const Icon(Icons.logout),
              onPressed: () async {
                await FirebaseAuth.instance.signOut();
              },
            ),
          ],
          // 下部にタブを表示
          bottom: const TabBar(
            tabs: [
              Tab(text: 'チャット'),
              Tab(text: 'タスク'),
            ],
          ),
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
                      color: Colors.blue,
                    ),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const Text(
                          '目標一覧',
                          style: TextStyle(color: Colors.white, fontSize: 24),
                        ),
                        Padding(
                          padding: const EdgeInsets.all(8.0),
                          child: AddGoalButton(viewModel: goalViewModel),
                        ),
                      ],
                    ),
                  ),
                ),
                // 目標一覧を表示する部分
                // ここはあなたのもともとのコードを利用
                StreamBuilder<QuerySnapshot>(
                  stream: chatViewModel.getGoalStream(userId),
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
                        final goalId = docs[index].id;
                        return ListTile(
                          title: Text(goal),
                          onTap: () {
                            // 目標を選択
                            chatViewModel.setSelectedGoalId(goalId);
                            Navigator.pop(context); // Drawer を閉じる
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
        body: TabBarView(
          children: [
            // 1枚目 (チャット)
            _ChatTabContent(
              userId: userId,
              chatViewModel: chatViewModel,
              goalViewModel: goalViewModel,
            ),
            // 2枚目 (タスクなど新しいレイアウト)
            TaskWidget(),
          ],
        ),
      ),
    );
  }
}

/// 1つ目のタブに表示するチャット用ウィジェットを分割
class _ChatTabContent extends StatelessWidget {
  const _ChatTabContent({
    Key? key,
    required this.userId,
    required this.chatViewModel,
    required this.goalViewModel,
  }) : super(key: key);

  final String userId;
  final ChatViewModel chatViewModel;
  final GoalViewModel goalViewModel;

  @override
  Widget build(BuildContext context) {
    final selectedGoalId = chatViewModel.selectedGoalId;
    final chatStream = chatViewModel.getChatStream(userId, selectedGoalId);

    return Column(
      children: [
        // メッセージ一覧 (既存コードを流用)
        Expanded(
          child: selectedGoalId != null
              ? StreamBuilder<QuerySnapshot>(
            stream: chatStream,
            builder: (context, snapshot) {
              if (!snapshot.hasData) {
                return const Center(child: CircularProgressIndicator());
              }
              final docs = snapshot.data!.docs;
              final isEmpty = docs.isEmpty;
              // チャットが空の場合は FirstInputWidget
              if (isEmpty) {
                return FirstInputWidget(
                  chatViewModel: chatViewModel,
                  userId: userId,
                  goalId: selectedGoalId,
                );
              } else {
                // 既にチャットが存在する場合
                return const SizedBox();
              }
            },
          )
              : Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Text('目標を選択してください'),
                AddGoalButton(viewModel: goalViewModel),
              ],
            ),
          ),
        ),
        // 入力欄
        StreamBuilder<QuerySnapshot>(
          stream: chatStream,
          builder: (context, snapshot) {
            if (!snapshot.hasData) {
              return const SizedBox();
            }
            final docs = snapshot.data!.docs;
            final notEmpty = docs.isNotEmpty;
            final hasGoalId = selectedGoalId != null;
            if (hasGoalId && notEmpty) {
              return ChatInputArea(chatViewModel: chatViewModel);
            } else {
              return const SizedBox();
            }
          },
        ),
      ],
    );
  }
}

