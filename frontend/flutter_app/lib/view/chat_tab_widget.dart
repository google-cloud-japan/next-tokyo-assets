import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:hackathon_test1/view/common/input_with_send_button.dart';
import 'package:hackathon_test1/viewmodel/chat_viewmodel.dart';

import 'first_input_widget.dart';

class ChatTabWidget extends ConsumerWidget {
  final TextEditingController _messageController = TextEditingController();

  ChatTabWidget({
    super.key,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final user = FirebaseAuth.instance.currentUser;
    if (user == null) {
      return const Center(child: Text('ログインしていません'));
    }

    final chatViewModel = ref.watch(chatViewModelProvider);
    final userId = user.uid;
    final selectedGoalId = chatViewModel.selectedGoalId;

    // ① 目標がまだ選択されていない場合
    if (selectedGoalId == null) {
      return const Center(child: Text('目標を選択してください'));
    }

    // チャットのStream
    final chatStream = chatViewModel.getChatStream(userId, selectedGoalId);

    return Column(
      children: [
        // メッセージ一覧表示部分
        Expanded(
          child: StreamBuilder<QuerySnapshot>(
            stream: chatStream,
            builder: (context, snapshot) {
              if (snapshot.connectionState == ConnectionState.waiting) {
                return const Center(child: CircularProgressIndicator());
              }
              if (!snapshot.hasData || snapshot.data!.docs.isEmpty) {
                // チャットが空 → FirstInputWidget
                return FirstInputWidget(
                  chatViewModel: chatViewModel,
                  userId: userId,
                  goalId: selectedGoalId,
                );
              }

              final docs = snapshot.data!.docs;
              return Stack(
                children: [
                  Padding(
                    padding: const EdgeInsets.only(bottom: 80),
                    child: ListView.builder(
                      physics: const AlwaysScrollableScrollPhysics(),
                      padding: const EdgeInsets.all(8),
                      itemCount: docs.length,
                      itemBuilder: (context, index) {
                        final data = docs[index].data() as Map<String, dynamic>;
                        final content = data['content'] as String? ?? '';
                        final role = data['role'] as String? ?? 'user';
                        final createdAt = data['createdAt'];
                        DateTime? createdTime;
                        if (createdAt is Timestamp) {
                          createdTime = createdAt.toDate();
                        }

                        return _buildChatBubble(
                          content: content,
                          role: role,
                          createdTime: createdTime,
                        );
                      },
                    ),
                  ),
                  Padding(
                    padding: const EdgeInsets.only(bottom: 8.0),
                    child: Align(
                      alignment: Alignment.bottomCenter,
                      child: InputWithSendButton(
                        hintText: '目標を入力してください',
                        controller: _messageController,
                        onPressed: () async {
                          final messageText = _messageController.text.trim();

                          if (messageText.isEmpty) {
                            ScaffoldMessenger.of(context).showSnackBar(
                              const SnackBar(content: Text('チャットを入力してください')),
                            );
                            return;
                          }

                          try {
                            await chatViewModel.addMessage(
                              context: context,
                              userId: userId,
                              goalId: selectedGoalId,
                              message: messageText,
                            );
                          } catch (e) {
                            ScaffoldMessenger.of(context).showSnackBar(
                              SnackBar(content: Text('入力値が不正です: $e')),
                            );
                          } finally {
                            _messageController.clear();
                          }
                        },
                        iconImage: Icons.send,
                      ),
                    ),
                  ),
                ],
              );
            },
          ),
        ),
        // 画面下部の入力欄 (既存 ChatInputArea など)
        // (チャットが空のときは FirstInputWidget を表示するロジックがあるなら適宜書き換える)
      ],
    );
  }

  /// role によって左・右に分けたチャットバブルを作る例
  Widget _buildChatBubble({
    required String content,
    required String role,
    DateTime? createdTime,
  }) {
    // 自分(user)なら右、assistant なら左
    final bool isUser = (role == 'user');

    return Container(
      margin: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment:
            isUser ? MainAxisAlignment.end : MainAxisAlignment.start,
        children: [
          // バブル部分
          Container(
            padding: const EdgeInsets.all(12),
            constraints: const BoxConstraints(maxWidth: 250), // 横幅を抑える
            decoration: BoxDecoration(
              color: isUser ? Colors.blue[200] : Colors.grey[300],
              borderRadius: BorderRadius.circular(16),
            ),
            child: Column(
              crossAxisAlignment:
                  isUser ? CrossAxisAlignment.end : CrossAxisAlignment.start,
              children: [
                Text(
                  content,
                  style: const TextStyle(fontSize: 16),
                ),
                if (createdTime != null)
                  Text(
                    // 時刻部分を小さく表示
                    _formatTime(createdTime),
                    style: TextStyle(fontSize: 12, color: Colors.grey[600]),
                  ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  // 送信時刻のフォーマット例
  String _formatTime(DateTime dateTime) {
    // 好きな書式に変えてください (例: 2025/01/31 18:00)
    return '${dateTime.year}/${dateTime.month.toString().padLeft(2, '0')}/${dateTime.day.toString().padLeft(2, '0')} '
        '${dateTime.hour.toString().padLeft(2, '0')}:${dateTime.minute.toString().padLeft(2, '0')}';
  }
}
