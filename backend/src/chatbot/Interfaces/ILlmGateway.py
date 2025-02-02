from dataclasses import dataclass
from typing import List, Optional, Protocol

from Domain.Models.Chat import ChatMessage


@dataclass(frozen=True)
class GenerationResult:
    data: Optional[dict]  # 任意のデータを格納
    message: Optional[str]
    succeed: bool
    errorMessage: Optional[str]

    @classmethod
    def success(
        cls, data: dict, message: str = "処理が正常に完了しました"
    ) -> "GenerationResult":
        if not data:
            raise ValueError("成功時はデータ必須")
        return cls(
            succeed=True,
            data=data,
            message=message,
            errorMessage=None
        )

    @classmethod
    def error(cls, errorMessage: str, llmResponse: str = None) -> "GenerationResult":
        return cls(
            succeed=False,
            data=None,
            message=None,
            errorMessage=errorMessage
        )


class ILlmGateway(Protocol):
    """LLMとの通信を抽象化するインターフェース"""

    def generateTask(self, prompt: str, context: List[ChatMessage]) -> GenerationResult:
        """
        プロンプトとコンテキストからLLMを使用して応答を生成する

        Args:
            prompt: ユーザーからの入力テキスト
            context: 会話の文脈情報

        Returns:
            生成された応答（タスクリストまたは確認要求）
        """
        ...

    def generateMessage(
        self, prompt: str, context: List[ChatMessage]
    ) -> GenerationResult:
        """
        プロンプトとコンテキストからLLMを使用して応答を生成する

        Args:
            prompt: ユーザーからの入力テキスト
            context: 会話の文脈情報
        """
        ...
