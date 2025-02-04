import 'package:flutter/material.dart';

class InputWithSendButton extends StatelessWidget {
  final String _hintText;
  final TextEditingController _controller;
  final VoidCallback _onPressed;
  final IconData _iconImage;

  const InputWithSendButton({
    super.key,
    required String hintText,
    required TextEditingController controller,
    required void Function() onPressed,
    required IconData iconImage,
  })  : _onPressed = onPressed,
        _controller = controller,
        _hintText = hintText,
        _iconImage = iconImage;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Container(
          height: 60,
          width: MediaQuery.of(context).size.width * 0.8,
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: Colors.grey),
          ),
          child: TextField(
            controller: _controller,
            decoration: InputDecoration(
              hintText: _hintText,
              border: InputBorder.none,
              contentPadding: const EdgeInsets.symmetric(
                horizontal: 16,
                vertical: 16,
              ),
            ),
          ),
        ),
        const SizedBox(width: 8),
        Container(
          height: 50,
          width: 50,
          decoration: BoxDecoration(
            color: Colors.blue, // 背景色を青色に設定
            borderRadius: BorderRadius.circular(8.0), // 必要であれば、角を丸める
          ),
          child: IconButton(
            icon: Icon(
              _iconImage,
              color: Colors.white,
            ),
            onPressed: _onPressed, // コールバック関数を渡す
          ),
        ),
      ],
    );
  }
}
