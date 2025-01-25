import logging
from typing import Dict

from Repositories.ChatRepository import ChatRepository
from Services.ChatService import ChatService
from UseCases.ObjectiveUseCaseInput import ObjectiveUseCaseInput

logger = logging.getLogger(__name__)


class ObjectiveUseCase:
    """目標設定に関するユースケースを担当するクラス"""

    def __init__(self, chat_service: ChatService, chat_repository: ChatRepository):
        """
        ObjectiveUseCaseの初期化

        Args:
            chat_service: チャットサービス
            chat_repository: チャットリポジトリ
        """
        self.chat_service = chat_service
        self.chat_repository = chat_repository
        logger.info("Initialized ObjectiveUseCase")

    def generate(self, input: ObjectiveUseCaseInput) -> Dict[str, str]:
        """
        目標を達成するためのアクションを生成する

        Args:
            input: 目標生成の入力データ

        Returns:
            生成されたアクションを含む辞書
        """
        # チャット履歴を取得
        chat_history = []
        if input.objective_id:
            chat_history = self.chat_repository.findByObjectiveId(input.objective_id)
            logger.info(f"Retrieved chat history for objective {input.objective_id}")

        # チャットサービスを使用してアクションを生成
        result = self.chat_service.generate_response(input.prompt, chat_history)

        if result["status"] == "success" and input.objective_id:
            # objective_idを追加
            result["objective_id"] = input.objective_id
            # 応答を保存
            # self.chat_repository.save(result)
            logger.info("Saved response to repository")

        if result["status"] == "success":
            logger.info("Successfully generated objective actions")
        else:
            logger.error("Failed to generate objective actions")

        return result
