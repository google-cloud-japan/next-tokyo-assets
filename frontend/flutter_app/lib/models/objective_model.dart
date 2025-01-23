import 'package:cloud_firestore/cloud_firestore.dart';

class Objective {
  final String id;
  final String objective;
  final DateTime createdAt;

  Objective(
      {required this.id, required this.objective, required this.createdAt});

  factory Objective.fromMap(Map<String, dynamic> data, String documentId) {
    return Objective(
      id: documentId,
      objective: data['objective'] ?? '',
      createdAt: (data['createdAt'] as Timestamp).toDate(),
    );
  }

  Map<String, dynamic> toMap() {
    return {
      'objective': objective,
      'createdAt': createdAt,
    };
  }
}
