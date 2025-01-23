import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/material.dart';
import 'package:hackathon_test1/models/objective_model.dart';

class ObjectiveViewModel {
  final FirebaseFirestore _firestore = FirebaseFirestore.instance;

  Future<void> addObjective(String objective, BuildContext context) async {
    final currentUser = FirebaseAuth.instance.currentUser;
    if (currentUser == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('ログインしていません')),
      );
      return;
    }

    try {
      final objectiveId = _firestore
          .collection('users')
          .doc(currentUser.uid)
          .collection('objectives')
          .doc()
          .id;
      final newObjective = Objective(
        id: objectiveId,
        objective: objective,
        createdAt: DateTime.now(),
      );
      await _firestore
          .collection('users')
          .doc(currentUser.uid)
          .collection('objectives')
          .doc(objectiveId)
          .set(newObjective.toMap());
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('目標が追加されました')),
      );
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Firestore書き込みエラー: $e')),
      );
    }
  }
}
