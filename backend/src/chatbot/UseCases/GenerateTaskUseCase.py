import logging
from dataclasses import dataclass
from typing import List, Optional

from Domain.Models.Chat import ChatMessage, ChatRole
from Repositories.ChatRepository import ChatHistoryRepository
from Services.ChatService import ChatService

logger = logging.getLogger(__name__)


class GenerateTaskUseCase:
    """タスク生成に関するユースケースを担当するクラス"""

    @dataclass
    class Input:

        prompt: str  # ユーザーからの入力テキスト
        userId: str  # ユーザーID Firebase Auth ID
        goalId: Optional[str] = None  # 目標を識別するためのID
        deadline: Optional[str] = None  # 目標の期日 (YYYY-MM-DD形式) 目標をいつまでに達成したいか
        weeklyHours: Optional[int] = None  # 週あたりの作業時間 (時間) 目標を達成するために1週間にかける時間

    @dataclass
    class Output:

        status: str  # "success" または "error" または "please_retype_prompt"
        message: str  # ユーザーに表示するメッセージ
        tasks: Optional[List[dict]] = None  # タスクのリスト（成功時のみ存在）
        errorMessage: Optional[str] = None  # エラーメッセージ（エラー時のみ存在）

    def __init__(self, chatService: ChatService, chatHistoryRepository: ChatHistoryRepository):
        """

        Args:
            chatService: チャットサービス
            chatRepository: チャットリポジトリ
        """
        self.chatService = chatService
        self.chatHistoryRepository = chatHistoryRepository

    def generate(self, input: Input) -> Output:
        """
        目標を達成するためのアクションを生成する

        Args:
            input: 目標生成の入力データ

        Returns:
            生成されたアクションを含むOutput
        """
        # 回答を生成する際は過去のやりとりも考慮してもらうので目標IDから過去のやりとりを取得する
        chatHistory = []
        chatHistory = self.chatHistoryRepository.findByGoalIdForUser(
            userId=input.userId,
            goalId=input.goalId,
        )
        logger.info(f"chatHistory: {chatHistory}")
        try:
            # LLMにプロンプトと過去のやりとりを渡してタスクを生成してもらう
            chatServiceInput = self.chatService.GenerateResponseInput(prompt=input.prompt, chatHistory=chatHistory)
            # タスクを生成する
            result = self.chatService.generateResponse(chatServiceInput)
            logger.info(f"Result: {result}")
            if result.status == "error":
                logger.error(f"Error {result.error_code}: {result.message}")
                return self.Output(
                    status="error",
                    message=result.message,
                    errorMessage=result.error,
                )
            # ユーザが入力したプロンプトが目標でなかった場合
            if not result.succeed:
                return self.Output(
                    status="please_retype_prompt",
                    message=result.message,
                    errorMessage=result.error,
                )
            # ユーザーのプロンプトとLLMの回答結果を保存する
            chatMessages = []
            chatMessages.append(
                ChatMessage(
                    role=ChatRole.USER,
                    content=input.prompt,
                )
            )

            chatMessages.append(
                ChatMessage(
                    role=ChatRole.ASSISTANT,
                    content=result.message,
                    tasks=result.tasks,
                )
            )
            self.chatHistoryRepository.add(chatMessages, input.userId, input.goalId)
            logger.info("Saved response to repository")


            # 成功の場合
            return self.Output(
                status="success",
                message=result.message,
                tasks=result.tasks.toDict() if result.tasks else None
            )

        except Exception as e:
            logger.error(f"Error in generate: {e}", exc_info=True)
            return self.Output(status="error", errorMessage=str(e),message="エラーが発生しました。")
