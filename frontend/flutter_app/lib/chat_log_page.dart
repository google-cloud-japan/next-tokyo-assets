import 'package:flutter/material.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart';

class ChatLogPage extends StatelessWidget {
  final String objectiveId;

  const ChatLogPage({super.key, required this.objectiveId});

  @override
  Widget build(BuildContext context) {
    final currentUser = FirebaseAuth.instance.currentUser;
    if (currentUser == null) {
      return const Scaffold(
        body: Center(child: Text('ログインしていません')),
      );
    }

    final chatStream = FirebaseFirestore.instance
        .collection('users')
        .doc(currentUser.uid)
        .collection('objectives')
        .doc(objectiveId)
        .collection('chat')
        .orderBy('createdAt', descending: true)
        .snapshots();

    return Scaffold(
      appBar: AppBar(
        title: const Text('Chat Log'),
      ),
      body: StreamBuilder<QuerySnapshot>(
        stream: chatStream,
        builder: (context, snapshot) {
          if (!snapshot.hasData) {
            return const Center(child: CircularProgressIndicator());
          }
          final docs = snapshot.data!.docs;
          return ListView.builder(
            reverse: true,
            itemCount: docs.length,
            itemBuilder: (context, index) {
              final data = docs[index].data() as Map<String, dynamic>;
              final content = data['content'] ?? 'No Message';
              final createdAt =
                  data['createdAt']?.toDate().toString() ?? 'No Time';

              return ListTile(
                title: Text(content),
                subtitle: Text(createdAt),
              );
            },
          );
        },
      ),
    );
  }
}
