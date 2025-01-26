// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'user_credentials.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
    'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models');

UserCredentials _$UserCredentialsFromJson(Map<String, dynamic> json) {
  return _UserCredentials.fromJson(json);
}

/// @nodoc
mixin _$UserCredentials {
  String get email => throw _privateConstructorUsedError;
  String get password => throw _privateConstructorUsedError;

  /// Serializes this UserCredentials to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of UserCredentials
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $UserCredentialsCopyWith<UserCredentials> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $UserCredentialsCopyWith<$Res> {
  factory $UserCredentialsCopyWith(
          UserCredentials value, $Res Function(UserCredentials) then) =
      _$UserCredentialsCopyWithImpl<$Res, UserCredentials>;
  @useResult
  $Res call({String email, String password});
}

/// @nodoc
class _$UserCredentialsCopyWithImpl<$Res, $Val extends UserCredentials>
    implements $UserCredentialsCopyWith<$Res> {
  _$UserCredentialsCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of UserCredentials
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? email = null,
    Object? password = null,
  }) {
    return _then(_value.copyWith(
      email: null == email
          ? _value.email
          : email // ignore: cast_nullable_to_non_nullable
              as String,
      password: null == password
          ? _value.password
          : password // ignore: cast_nullable_to_non_nullable
              as String,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$UserCredentialsImplCopyWith<$Res>
    implements $UserCredentialsCopyWith<$Res> {
  factory _$$UserCredentialsImplCopyWith(_$UserCredentialsImpl value,
          $Res Function(_$UserCredentialsImpl) then) =
      __$$UserCredentialsImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({String email, String password});
}

/// @nodoc
class __$$UserCredentialsImplCopyWithImpl<$Res>
    extends _$UserCredentialsCopyWithImpl<$Res, _$UserCredentialsImpl>
    implements _$$UserCredentialsImplCopyWith<$Res> {
  __$$UserCredentialsImplCopyWithImpl(
      _$UserCredentialsImpl _value, $Res Function(_$UserCredentialsImpl) _then)
      : super(_value, _then);

  /// Create a copy of UserCredentials
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? email = null,
    Object? password = null,
  }) {
    return _then(_$UserCredentialsImpl(
      email: null == email
          ? _value.email
          : email // ignore: cast_nullable_to_non_nullable
              as String,
      password: null == password
          ? _value.password
          : password // ignore: cast_nullable_to_non_nullable
              as String,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$UserCredentialsImpl implements _UserCredentials {
  const _$UserCredentialsImpl({required this.email, required this.password});

  factory _$UserCredentialsImpl.fromJson(Map<String, dynamic> json) =>
      _$$UserCredentialsImplFromJson(json);

  @override
  final String email;
  @override
  final String password;

  @override
  String toString() {
    return 'UserCredentials(email: $email, password: $password)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$UserCredentialsImpl &&
            (identical(other.email, email) || other.email == email) &&
            (identical(other.password, password) ||
                other.password == password));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, email, password);

  /// Create a copy of UserCredentials
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$UserCredentialsImplCopyWith<_$UserCredentialsImpl> get copyWith =>
      __$$UserCredentialsImplCopyWithImpl<_$UserCredentialsImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$UserCredentialsImplToJson(
      this,
    );
  }
}

abstract class _UserCredentials implements UserCredentials {
  const factory _UserCredentials(
      {required final String email,
      required final String password}) = _$UserCredentialsImpl;

  factory _UserCredentials.fromJson(Map<String, dynamic> json) =
      _$UserCredentialsImpl.fromJson;

  @override
  String get email;
  @override
  String get password;

  /// Create a copy of UserCredentials
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$UserCredentialsImplCopyWith<_$UserCredentialsImpl> get copyWith =>
      throw _privateConstructorUsedError;
}
