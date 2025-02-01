import logging
from dataclasses import dataclass
from typing import Optional

from Services.Chat import ChatMessageGeneratorService

from Domain.Models.Chat import ChatMessage, ChatRole
from Repositories.ChatRepository import ChatHistoryRepository

logger = logging.getLogger(__name__)


class ChatQuestioningUseCase:
    @dataclass
    class Input:
        prompt: str  # ユーザーからの入力テキスト
        userId: str  # ユーザーID Firebase Auth ID
        goalId: Optional[str] = None  # 目標を識別するためのID

    @dataclass
    class Output:
        status: str  # "success" または "error" または "please_retype_prompt"
        message: str  # ユーザーに表示するメッセージ
        errorMessage: Optional[str] = None  # エラーメッセージ（エラー時のみ存在）


    def __init__(
        self,
        chatMessageGeneratorService: ChatMessageGeneratorService,
        chatHistoryRepository: ChatHistoryRepository
    ):

        self.chatMessageGeneratorService = chatMessageGeneratorService
        self.chatHistoryRepository = chatHistoryRepository

    def generate(self, input: Input) -> Output:
        """
        ユーザがチャットで質問をする

        処理の流れ
        ・チャットの履歴を復元する
        ・LLMに質問に対しての回答をしてもらう
        ・回答を保存する
        """

        # 過去のやりとりを考慮した回答を生成したいため、過去のやりとりを取得する
        chatHistory = self.chatHistoryRepository.findByGoalIdForUser(
            userId=input.userId,
            goalId=input.goalId,
        )
        logger.info(f"chatHistory: {chatHistory}")
        try:
            # LLMにプロンプトと過去のやりとりを渡してタスクを生成してもらう
            chatServiceInput = self.chatMessageGeneratorService.GenerateResponseInput(
                prompt=input.prompt,
                chatHistory=chatHistory
            )

            result = self.chatMessageGeneratorService.generate(chatServiceInput)
            logger.info(f"Result: {result}")
            if result.status == "error":
                logger.error(f"Error {result.error}: {result.message}")
                return self.Output(
                    status="error",
                    message=result.message,
                    errorMessage=result.error,
                )

            if not result.succeed:
                return self.Output(
                    status="please_retype_prompt",
                    message=result.message,
                    errorMessage=result.error,
                )

            chatMessages = []
            chatMessages.append(
                ChatMessage(
                    role=ChatRole.ASSISTANT,
                    content=result.message,
                    tasks=result.tasks,
                )
            )
            self.chatHistoryRepository.add(chatMessages, input.userId, input.goalId)



            # 成功の場合
            return self.Output(
                status="success",
                message=result.message,
            )

        except Exception as e:
            logger.error(f"Error in generate: {e}", exc_info=True)
            return self.Output(
                status="error", errorMessage=str(e), message="エラーが発生しました。"
            )
