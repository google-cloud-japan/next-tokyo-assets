import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:hackathon_test1/view/chat_tab_widget.dart';
import 'package:hackathon_test1/view/common/add_goal_button.dart';
import 'package:hackathon_test1/view/tasks_tab_widget.dart';
import 'package:hackathon_test1/viewmodel/chat_viewmodel.dart';
import 'package:hackathon_test1/viewmodel/goal_viewmodel.dart';

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
          title: Text(chatViewModel.selectedGoalText ?? 'Task Trail'),
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
                    decoration: const BoxDecoration(
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
                            chatViewModel.setSelectedGoalId(goalId, goal);
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
            ChatTabWidget(),
            // 2枚目 (タスクなど新しいレイアウト)
            const TaskTabWidget(),
          ],
        ),
      ),
    );
  }
}
