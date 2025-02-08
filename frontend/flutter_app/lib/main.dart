import 'package:firebase_core/firebase_core.dart';
import 'package:flutter/material.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:hackathon_test1/firebase/firebase_options.dart';
import 'package:permission_handler/permission_handler.dart';

import 'view/auth_gate.dart'; // AuthGate に分割
import 'view/chat_page.dart'; // チャット画面

final FlutterLocalNotificationsPlugin flutterLocalNotificationsPlugin = FlutterLocalNotificationsPlugin();

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // (1) 初期化設定
  const AndroidInitializationSettings initializationSettingsAndroid =
  AndroidInitializationSettings('@mipmap/ic_launcher');

  final InitializationSettings initializationSettings =
  InitializationSettings(android: initializationSettingsAndroid);

  // (2) プラグインの初期化
  await flutterLocalNotificationsPlugin.initialize(
    initializationSettings,
  );

  // 実行時に権限をリクエスト
  await requestNotificationPermission();

  await Firebase.initializeApp(
    options: DefaultFirebaseOptions.currentPlatform,
  );
  runApp(
    const ProviderScope(
      child: MyApp(),
    ),
  );
}

Future<void> requestNotificationPermission() async {
  // Android 13(API 33)以上の場合、notificationの権限を要求
  // それ未満のOSでは常にgrantedになる（パーミッションが無いため）
  final status = await Permission.notification.request();

  if (status.isGranted) {
    // ユーザーが通知許可した
    debugPrint('通知許可が与えられました');
  } else if (status.isDenied) {
    // ユーザーが「拒否」を選択
    debugPrint('通知許可が拒否されました(まだリクエスト可能)');
  } else if (status.isPermanentlyDenied) {
    // 「今後表示しない」(設定画面から手動で変更が必要)
    debugPrint('通知許可が永久に拒否されました。設定から有効化してください。');
    openAppSettings(); // permission_handlerでアプリ設定画面を開ける
  }
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Task Trail',
      theme: ThemeData(
        scaffoldBackgroundColor: Colors.white,
        appBarTheme: const AppBarTheme(
          backgroundColor: Colors.white,
          elevation: 0,
          iconTheme: IconThemeData(color: Colors.black),
        ),
        primarySwatch: Colors.blue,
        elevatedButtonTheme: ElevatedButtonThemeData(
          style: ElevatedButton.styleFrom(
            backgroundColor: Colors.blue,
            foregroundColor: Colors.white,
          ),
        ),
      ),
      initialRoute: '/',
      routes: {
        '/': (context) => const AuthGate(),
        '/chat': (context) => const ChatPage(),
      },
    );
  }
}
