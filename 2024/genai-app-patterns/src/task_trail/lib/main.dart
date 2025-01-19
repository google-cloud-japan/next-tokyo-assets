import 'package:flutter/material.dart';

void main() {
  runApp(const TaskTrail());
}

class TaskTrail extends StatelessWidget {
  const TaskTrail({super.key});

  // This widget is the root of your application.
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Task Trail',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
        primarySwatch: Colors.blue,
        useMaterial3: true,
      ),
      darkTheme: ThemeData.dark(),
      home: const RootLayout(),
    );
  }
}

class RootLayout extends StatelessWidget {
  const RootLayout({super.key});
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Task Trail'),
      ),
      body: const Center(
        child: Text('Upload own assets and expand your AI'),
      ),
    );
  }
}
