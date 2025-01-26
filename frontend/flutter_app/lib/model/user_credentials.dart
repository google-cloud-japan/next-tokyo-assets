// lib/model/user_credentials.dart
import 'package:freezed_annotation/freezed_annotation.dart';

part 'user_credentials.freezed.dart';
part 'user_credentials.g.dart';

@freezed
class UserCredentials with _$UserCredentials {
  const factory UserCredentials({
    required String email,
    required String password,
  }) = _UserCredentials;

  factory UserCredentials.fromJson(Map<String, dynamic> json) =>
      _$UserCredentialsFromJson(json);
}

extension UserCredentialsExtension on UserCredentials {
  bool get isValid => email.isNotEmpty && password.isNotEmpty;
}
