import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:hackathon_test1/viewmodel/chat_viewmodel.dart';

/// 2つ目のタブ用のレイアウトサンプル
class TaskWidget extends ConsumerWidget {
  const TaskWidget({
    super.key,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // 現在ログイン中のユーザー
    final user = FirebaseAuth.instance.currentUser;
    if (user == null) {
      // ログインしていない場合
      return const Center(child: Text('ログインしていません'));
    }

    final chatViewModel = ref.watch(chatViewModelProvider);
    final userId = user.uid;
    final selectedGoalId = chatViewModel.selectedGoalId;

    // タスク一覧を取得する Stream
    final tasksStream = chatViewModel.getTasksStream(userId, selectedGoalId);

    // タスク一覧を表示
    return StreamBuilder<QuerySnapshot>(
      stream: tasksStream,
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          // データ待ちのローディング中
          return const Center(child: CircularProgressIndicator());
        }
        if (!snapshot.hasData) {
          return const Center(child: Text('タスクがありません'));
        }

        final docs = snapshot.data!.docs;
        if (docs.isEmpty) {
          return const Center(child: Text('タスクがありません'));
        }

        // タスクのリストを表示
        return ListView.builder(
          itemCount: docs.length,
          itemBuilder: (context, index) {
            final data = docs[index].data() as Map<String, dynamic>;

            // Firestore の項目
            final title = data['title'] as String? ?? 'No Title';
            final description = data['description'] as String? ?? '';
            final priority = data['priority'] as int? ?? 0;
            final deadline = data['deadline']; // Timestamp 形式の場合あり
            final createdAt = data['created_at']; // Timestamp 形式の場合あり
            final requiredTime = data['requiredTime'] as int? ?? 0;

            // Timestamp から DateTime への変換例（Firestore の Timestamp の場合）
            DateTime? deadlineDate;
            if (deadline != null && deadline is Timestamp) {
              deadlineDate = deadline.toDate();
            }

            DateTime? createdDate;
            if (createdAt != null && createdAt is Timestamp) {
              createdDate = createdAt.toDate();
            }

            return ListTile(
              title: Text(title),
              subtitle: Text(
                '優先度: $priority\n'
                '必要な時間: $requiredTime 時間\n'
                '締め切り: ${deadlineDate?.toLocal() ?? '-'}\n'
                '作成日: ${createdDate?.toLocal() ?? '-'}\n'
                '$description',
              ),
              // それぞれのタスクをタップしたときの処理など
              onTap: () {
                // 例: 詳細画面へ遷移するなど
              },
            );
          },
        );
      },
    );
  }
}
