import 'package:flutter/material.dart';
import 'package:hackathon_test1/viewmodel/goal_viewmodel.dart';

class AddGoalButton extends StatelessWidget {
  final GoalViewModel viewModel;

  const AddGoalButton({super.key, required this.viewModel});

  @override
  Widget build(BuildContext context) {
    return ElevatedButton.icon(
      onPressed: () {
        showDialog(
          context: context,
          builder: (BuildContext context) {
            final TextEditingController goalController =
                TextEditingController();
            return AlertDialog(
              title: const Text('新規目標追加'),
              content: TextField(
                controller: goalController,
                decoration: const InputDecoration(
                  hintText: '目標を入力してください',
                ),
              ),
              actions: [
                TextButton(
                  onPressed: () {
                    Navigator.of(context).pop();
                  },
                  child: const Text('キャンセル'),
                ),
                TextButton(
                  onPressed: () {
                    final goal = goalController.text.trim();
                    if (goal.isNotEmpty) {
                      viewModel.addGoal(goal, context);
                    }
                    Navigator.of(context).pop();
                  },
                  child: const Text('追加'),
                ),
              ],
            );
          },
        );
      },
      icon: const Icon(Icons.add),
      label: const Text('新規目標'),
    );
  }
}
