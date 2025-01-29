// lib/viewmodel/chat_viewmodel.dart
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:hackathon_test1/model/chat_message.dart';
import 'package:hackathon_test1/view/common/snackbar_helper.dart';

final chatViewModelProvider = ChangeNotifierProvider((ref) => ChatViewModel());

class ChatViewModel extends ChangeNotifier {
  final FirebaseFirestore _firestore = FirebaseFirestore.instance;
  final TextEditingController textController = TextEditingController();
  String? selectedGoalId;

  // メッセージを Firestore に追加
  Future<void> addMessage(String notebookId, BuildContext context) async {
    final text = textController.text.trim();
    if (text.isEmpty) return;

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
          .add(ChatMessage(
            content: text,
            role: "user",
            createdAt: DateTime.now(),
          ).toJson());
      textController.clear();
      SnackbarHelper.show(context, 'メッセージが送信されました');
    } catch (e) {
      SnackbarHelper.show(context, 'Firestore 書き込みエラー: $e');
    }
  }

  // チャットメッセージの Stream を取得
  Stream<QuerySnapshot<Object?>>? getChatStream(String userId, String? goalId) {
    if (goalId == null) return const Stream.empty();
    return _firestore
        .collection('users')
        .doc(userId)
        .collection('goals')
        .doc(goalId)
        .collection('chat')
        .orderBy('createdAt', descending: true)
        .snapshots();
  }

  // 目標の Stream を取得
  Stream<QuerySnapshot<Object?>>? getGoalStream(String userId) {
    return _firestore
        .collection('users')
        .doc(userId)
        .collection('goals')
        .orderBy('createdAt', descending: true)
        .snapshots();
  }

  void setSelectedGoalId(String goalId) {
    selectedGoalId = goalId;
    notifyListeners();
  }

  /// まだチャットが存在しない場合に初回送信時: 期日、週あたり作業時間、最初のメッセージをまとめて保存
  Future<void> addGoalDataAndFirstMessage({
    required BuildContext context,
    required String userId,
    required String goalId,
    required DateTime deadline,
    required double weeklyHours,
    required String message,
  }) async {
    final currentUser = FirebaseAuth.instance.currentUser;
    if (currentUser == null) {
      SnackbarHelper.show(context, 'ログインしていません');
      return;
    }

    try {
      // 1) goals/(goalId) ドキュメントに deadline, weeklyHours を保存
      await _firestore
          .collection('users')
          .doc(userId)
          .collection('goals')
          .doc(goalId)
          .update({
        'deadline': deadline,
        'weeklyHours': weeklyHours,
      });

      // 2) chat サブコレクションにメッセージを1件追加
      await _firestore
          .collection('users')
          .doc(userId)
          .collection('goals')
          .doc(goalId)
          .collection('chat')
          .add(ChatMessage(
        content: message,
        role: "user",
        createdAt: DateTime.now(),
      ).toJson());

      SnackbarHelper.show(context, '期日・作業時間・メッセージを保存しました');
    } catch (e) {
      SnackbarHelper.show(context, 'Firestore 書き込みエラー: $e');
    }
  }
}
