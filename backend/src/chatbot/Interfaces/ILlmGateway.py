from dataclasses import dataclass
from datetime import date
from typing import List, Optional, Protocol

from Domain.Models.Chat import ChatMessage
from Domain.Models.TaskCollection import TaskCollection

RESPONSE_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "status": {"type": "string"},
            "message": {"type": "string"},
            "tasks": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "description": {"type": "string"},
                        "deadline": {"type": "string"},
                        "requiredTime": {"type": "integer"},
                        "priority": {"type": "integer", "minimum": 1, "maximum": 5},
                    },
                    "required": ["title", "description", "deadline", "requiredTime", "priority"],
                },
            },
        },
        "required": ["status", "message", "tasks"],
    },
}


@dataclass(frozen=True)
class TaskGenerationResult:
    tasks: Optional[TaskCollection]
    llmResponse: Optional[str]
    succeed: bool
    errorMessage: Optional[str]

    @classmethod
    def success(cls, tasks: TaskCollection, llmResponse: str = "処理が正常に完了しました") -> "TaskGenerationResult":
        if not tasks:
            raise ValueError("成功時はタスクリスト必須")
        return cls(
            tasks=tasks,
            llmResponse=llmResponse,
            succeed=True,
            errorMessage=None
        )

    @classmethod
    def error(cls, errorMessage: str, llmResponse: str = None) -> "TaskGenerationResult":
        return cls(
            tasks=None,
            llmResponse=llmResponse,
            succeed=False,
            errorMessage=errorMessage
        )


class ILlmGateway(Protocol):
    """LLMとの通信を抽象化するインターフェース"""

    def generateTask(self, prompt: str, context: List[ChatMessage]) -> TaskGenerationResult:
        """
        プロンプトとコンテキストからLLMを使用して応答を生成する

        Args:
            prompt: ユーザーからの入力テキスト
            context: 会話の文脈情報

        Returns:
            生成された応答（タスクリストまたは確認要求）
        """
        ...
