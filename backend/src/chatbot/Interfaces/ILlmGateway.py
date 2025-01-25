from typing import List, Dict, Protocol


class ILlmGateway(Protocol):
    """LLMとの通信を抽象化するインターフェース"""
    
    def generate_content(self, prompt: str, context: List[Dict[str, str]]) -> str:
        """
        プロンプトとコンテキストからLLMを使用して応答を生成する

        Args:
            prompt: ユーザーからの入力テキスト
            context: 会話の文脈情報

        Returns:
            生成された応答テキスト
        """
        ... 