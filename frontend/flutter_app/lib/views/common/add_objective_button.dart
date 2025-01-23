import 'package:flutter/material.dart';
import 'package:hackathon_test1/viewmodels/objective_viewmodel.dart';

class AddObjectiveButton extends StatelessWidget {
  final ObjectiveViewModel viewModel;

  const AddObjectiveButton({super.key, required this.viewModel});

  @override
  Widget build(BuildContext context) {
    return ElevatedButton.icon(
      onPressed: () {
        showDialog(
          context: context,
          builder: (BuildContext context) {
            final TextEditingController objectiveController =
                TextEditingController();
            return AlertDialog(
              title: const Text('新規目標追加'),
              content: TextField(
                controller: objectiveController,
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
                    final objective = objectiveController.text.trim();
                    if (objective.isNotEmpty) {
                      viewModel.addObjective(objective, context);
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
