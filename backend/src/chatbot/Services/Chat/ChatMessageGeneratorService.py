import logging
from dataclasses import dataclass
from typing import List, Optional

from Domain.Models.Chat import ChatMessage
from Domain.Models.TaskCollection import TaskCollection
from Interfaces.ILlmGateway import ILlmGateway

logger = logging.getLogger(__name__)


class ChatService:
    """チャットボットのコアロジックを担当するクラス"""

    @dataclass
    class GenerateResponseInput:
        """チャット生成の入力データを表すクラス"""

        prompt: str  # ユーザーからの入力テキスト
        chatHistory: Optional[List[ChatMessage]] = None  # チャット履歴

    @dataclass
    class GenerateResponseOutput:
        """チャット生成の出力データを表すクラス"""

        status: str  # "success" または "error"
        succeed: bool  # 生成に成功したかどうか
        tasks: Optional[TaskCollection] = None  # タスクのリスト（成功時のみ存在）
        error: Optional[str] = None  # エラーメッセージ（エラー時のみ存在）
        message: Optional[str] = None  # メッセージ（成功時のみ存在）

    def __init__(self, llmGateway: ILlmGateway):
        """
        ChatServiceの初期化

        Args:
            llmGateway: LLMゲートウェイ
        """
        self.llmGateway = llmGateway
        logger.info("Initialized ChatService")

    def generateResponse(self, input: GenerateResponseInput) -> GenerateResponseOutput:
        try:
            # LLMを使用して応答を生成
            output = self.llmGateway.generateTask(input.prompt, input.chatHistory or [])
            return self.GenerateResponseOutput(
                status="success",
                succeed=output.succeed,
                tasks=output.tasks,
                message=output.llmResponse
            )

        except Exception as err:
            logger.error(f"Error in generate_response: {err}", exc_info=True)
            return self.GenerateResponseOutput(
                status="error",
                succeed=False,
                error="申し訳ございません。応答の生成に失敗しました。"
            )
