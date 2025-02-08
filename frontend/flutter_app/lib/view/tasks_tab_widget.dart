import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:hackathon_test1/repository/task_repository.dart';
import 'package:hackathon_test1/viewmodel/auth_viewmodel.dart';
import 'package:hackathon_test1/viewmodel/chat_viewmodel.dart';
import 'dart:convert';

/// 2つ目のタブ用のサンプルウィジェット
class TaskTabWidget extends ConsumerWidget {
  const TaskTabWidget({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final user = FirebaseAuth.instance.currentUser;
    if (user == null) {
      // ログインしていない場合
      return const Center(child: Text('ログインしていません'));
    }

    final chatViewModel = ref.watch(chatViewModelProvider);
    final authViewModel = ref.watch(authViewModelProvider);
    final userId = user.uid;
    final selectedGoalId = chatViewModel.selectedGoalId;
    final selectedGoalText = chatViewModel.selectedGoalText;

    // goalId が選択されていない場合
    if (selectedGoalId == null) {
      return const Center(child: Text('目標が選択されていません'));
    }

    // 1) ゴール1件のドキュメントをストリームで監視 (taskFixed の変化を追う)
    return StreamBuilder<DocumentSnapshot>(
      stream: chatViewModel.getGoalDocStream(userId, selectedGoalId),
      builder: (context, goalSnapshot) {
        if (goalSnapshot.connectionState == ConnectionState.waiting) {
          return const Center(child: CircularProgressIndicator());
        }
        if (!goalSnapshot.hasData || !goalSnapshot.data!.exists) {
          return const Center(child: Text('目標が存在しません'));
        }

        final goalDoc = goalSnapshot.data!;
        final data = goalDoc.data() as Map<String, dynamic>?;

        // taskFixed の値を取得 (なければ false 扱い)
        final bool isTaskFixed = data?['taskFixed'] as bool? ?? false;

        // 2) タスク一覧をストリームで取得
        final tasksStream = chatViewModel.getTasksStream(userId, selectedGoalId);
        return StreamBuilder<QuerySnapshot>(
          stream: tasksStream,
          builder: (context, tasksSnapshot) {
            if (tasksSnapshot.connectionState == ConnectionState.waiting) {
              return const Center(child: CircularProgressIndicator());
            }
            if (!tasksSnapshot.hasData) {
              return const Center(child: Text('タスクがありません'));
            }

            final docs = tasksSnapshot.data!.docs;
            if (docs.isEmpty) {
              // タスクコレクションが空の場合
              return const Center(child: Text('タスクがありません'));
            }

            // タスク一覧を表示するリスト
            final listTiles = List<Widget>.generate(docs.length, (index) {
              final data = docs[index].data() as Map<String, dynamic>;

              final title = data['title'] as String? ?? 'No Title';
              final description = data['description'] as String? ?? '';
              final priority = data['priority'] as int? ?? 0;
              final requiredTime = data['requiredTime'] as int? ?? 0;

              // Timestamp -> DateTime
              DateTime? deadlineDate;
              final deadline = data['deadline'];
              if (deadline is Timestamp) {
                deadlineDate = deadline.toDate();
              }

              DateTime? createdDate;
              final createdAt = data['createdAt'];
              if (createdAt is Timestamp) {
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
                onTap: () {
                  // タップ時の処理など
                },
              );
            });

            // 画面下にボタンを配置したいので Column
            return Column(
              children: [
                // タスクをリストで表示
                Expanded(
                  child: ListView(children: listTiles),
                ),

                // 「タスクを確定する」ボタン
                // isTaskFixed が falseの場合だけ表示
                if (!isTaskFixed)
                  Padding(
                    padding:
                    const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                    child: SizedBox(
                      width: double.infinity,
                      child: ElevatedButton(
                        onPressed: () async {
                          // goal ドキュメントに taskFixed = true を書き込む
                          await chatViewModel.updateTaskFixed(
                            userId: userId,
                            goalId: selectedGoalId,
                            taskFixed: true,
                          );
                          // 書き込み完了後、自動的に goal ドキュメントが更新されるため
                          // ここでのゴールスナップショットが再ビルドされ、isTaskFixed が true になってボタンが消える
                          String? token = authViewModel.accessToken;
                          await TaskRepository.fetchTasksAndPost(
                            authToken: token!,
                            userId: userId,
                            goalId: selectedGoalId,
                            goalText: selectedGoalText
                          );
                        },
                        child: const Text('タスクを確定する'),
                      ),
                    ),
                  ),
              ],
            );
          },
        );
      },
    );
  }
}
