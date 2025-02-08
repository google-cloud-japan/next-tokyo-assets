import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

class ThemeToggleButton extends StatefulWidget {
  const ThemeToggleButton({super.key});

  @override
  State<ThemeToggleButton> createState() => _ThemeToggleButtonState();
}

class _ThemeToggleButtonState extends State<ThemeToggleButton> {
  bool _isDarkMode = false; // ダークモードの状態

  @override
  void initState() {
    super.initState();
    _loadThemeMode(); // 保存されたテーマ設定を読み込む
  }

  Future<void> _loadThemeMode() async {
    final prefs = await SharedPreferences.getInstance();
    setState(() {
      _isDarkMode = prefs.getBool('isDarkMode') ?? false;
    });
  }

  Future<void> _saveThemeMode(bool isDarkMode) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool('isDarkMode', isDarkMode);
  }

  @override
  Widget build(BuildContext context) {
    return Switch(
      value: _isDarkMode,
      onChanged: (value) {
        setState(() {
          _isDarkMode = value;
          _saveThemeMode(value); // 設定を保存

          // ThemeDataにはchangeThemeメソッドはない。Themeウィジェットでラップする。
          // これにより、新しいテーマで下のウィジェットツリーが再構築される。
          if (_isDarkMode) {
            Theme.of(context).copyWith(
              scaffoldBackgroundColor: Colors.black,
              brightness: Brightness.dark,
            ); // 他のコンポーネントのために重要); // ダークテーマを適用
          } else {
            Theme.of(context).copyWith(
              scaffoldBackgroundColor: Colors.white,
              // ... 他のライトテーマ設定
              brightness: Brightness.light, // 他のコンポーネントのために重要
            );
          }
        });
      },
    );
  }
}
