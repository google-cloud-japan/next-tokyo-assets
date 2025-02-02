// lib/model/chat_message.dart
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:freezed_annotation/freezed_annotation.dart';

part 'chat_message.freezed.dart';
part 'chat_message.g.dart';

@freezed
class ChatMessage with _$ChatMessage {
  const factory ChatMessage({
    required String content,
    required String role,
    @JsonKey(name: 'created_at') DateTime? createdAt,
    @Default(false) bool loading,
    List<String>? ragFileIds,
    @Default('success') String status,
  }) = _ChatMessage;

  factory ChatMessage.fromJson(Map<String, dynamic> json) =>
      _$ChatMessageFromJson(json);

  factory ChatMessage.fromFirestore(DocumentSnapshot doc) {
    final data = doc.data() as Map<String, dynamic>;
    return ChatMessage.fromJson(data).copyWith(
      createdAt: (data['created_at'] as Timestamp?)?.toDate(),
    );
  }
}
