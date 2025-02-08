import 'package:cloud_firestore/cloud_firestore.dart';
import 'dart:convert';           // jsonEncode用
import 'package:http/http.dart' as http;
import 'package:flutter/material.dart';

class TaskRepository {
  final FirebaseFirestore _firestore = FirebaseFirestore.instance;

  /// userId と goalId を指定して、tasks コレクションのドキュメントを取得し、
  /// [
  ///   {
  ///     "title": "xxx",
  ///     "description": "yyy",
  ///     "deadline": "2025-03-01",
  ///     "requiredTime": 120
  ///   },
  ///   ...
  /// ]
  /// のような List<Map<String, dynamic>> を返す
  Future<List<Map<String, dynamic>>> getTasksAsJson({
    required String userId,
    required String goalId,
  }) async {
    // Firestore から tasks 一覧を取得
    final snapshot = await _firestore
        .collection('users')
        .doc(userId)
        .collection('goals')
        .doc(goalId)
        .collection('tasks')
        .get();

    // 取得したドキュメントを List<Map<String, dynamic>> に変換
    final List<Map<String, dynamic>> result = [];

    for (var doc in snapshot.docs) {
      final data = doc.data();

      // Firestoreに保存されているdeadlineがTimestampの場合はDateTimeに変換
      final deadlineStr = data['deadline'];

      // JSONとして必要なフィールドをまとめる
      result.add({
        "title": data["title"] ?? "",
        "description": data["description"] ?? "",
        "deadline": deadlineStr ?? "",       // なければ空文字に
        "requiredTime": data["requiredTime"] ?? 0,
      });
    }

    return result;
  }

  /// Firestoreからtasksを取得し、JSON化したデータをHTTP POSTする
  static Future<void> fetchTasksAndPost({
    required String authToken,
    required String userId,
    required String goalId,
    required String? goalText,
  }) async {
    final repo = TaskRepository();

    // 1) Firestoreからtasksを取得 → JSONのリストに変換
    final tasksJsonList = await repo.getTasksAsJson(userId: userId, goalId: goalId);

    if (goalText == null) {
      return;
    }

    // 2) JSON文字列に変換
    final requestBody = {
      "tasks": tasksJsonList,
      "goal": goalText,
    };
    final jsonString = jsonEncode(requestBody);

    // 3) HTTP POSTする
    const url = 'https://chatbot-api-514173068988.asia-northeast1.run.app/sync-tasks';
    // ローカル練習用
    // const url = 'http://192.168.1.49:8080/sync-tasks';
    try {
      final response = await http.post(
        Uri.parse(url),
        headers: {
          'Authorization': 'Bearer $authToken',  // Google Auth Token
          'Content-Type': 'application/json',
        },
        body: jsonString,
      );

      if (response.statusCode == 200) {
        debugPrint('POST 成功: ${response.body}');
      } else {
        debugPrint('POST 失敗: ${response.statusCode} ${response.reasonPhrase}');
        debugPrint('レスポンス: ${response.body}');
      }
    } catch (e) {
      debugPrint('POST エラー: $e');
    }
  }
}
