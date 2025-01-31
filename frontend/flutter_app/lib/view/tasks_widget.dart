import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:hackathon_test1/view/common/add_goal_button.dart';
import 'package:hackathon_test1/viewmodel/chat_viewmodel.dart';
import 'package:hackathon_test1/viewmodel/goal_viewmodel.dart';
import 'chat_input_widget.dart';
import 'first_input_widget.dart';

/// 2つ目のタブ用のレイアウトサンプル
class TaskWidget extends StatelessWidget {
  const TaskWidget({
    Key? key,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Text(
        'ここに新しいレイアウトやタスク一覧などを表示する',
        style: Theme.of(context).textTheme.titleLarge,
      ),
    );
  }
}
