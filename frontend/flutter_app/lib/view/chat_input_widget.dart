// lib/view/chat_page.dart
import 'package:flutter/material.dart';
import 'package:hackathon_test1/viewmodel/chat_viewmodel.dart';

class ChatInputArea extends StatelessWidget {
  final ChatViewModel chatViewModel;

  const ChatInputArea({
    Key? key,
    required this.chatViewModel,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
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
                  border: InputBorder.none, // デフォルトの枠線を削除
                  contentPadding: EdgeInsets.symmetric(
                    horizontal: 16,
                    vertical: 16,
                  ), // 内側の余白を設定
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
              // メッセージ送信
              chatViewModel.addMessage('tekitotekito', context);
            },
          ),
        ],
      ),
    );
  }
}
