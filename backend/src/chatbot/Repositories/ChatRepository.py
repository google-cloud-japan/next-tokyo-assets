import json
import logging
from datetime import datetime
from typing import Dict, List

from firebase_admin import credentials, firestore, initialize_app

from Config.DatabaseConfig import DatabaseConfig
from Domain.Models.Chat import ChatMessage
from Domain.Models.Task import Task
from Domain.Models.TaskCollection import TaskCollection

logger = logging.getLogger(__name__)


class ChatHistoryRepository:
    """Firestoreを使用したチャットデータの永続化を担当するクラス"""

    def __init__(self):

        try:
            cred = credentials.ApplicationDefault()
            logger.info(f"cred: {cred}")
            initialize_app(cred)
            self.db = firestore.client()
            logger.info("Firestore client initialized with default credentials")
        except Exception as e:
            logger.error(f"Firestore initialization failed: {e}")
            raise

    def add(self, chatMessages: List[ChatMessage], userId: str, goalId: str) -> None:
        try:
            for chatMessage in chatMessages:
                # ドメインモデルからFireStoreに保存するデータの形式に変換する
                chatMessageData = {
                    "role": chatMessage.role,
                    "content": chatMessage.content,
                    "created_at": chatMessage.createdAt.isoformat(),
                    "status": chatMessage.status,
                }
                # タスクがある場合はタスクを追加
                if chatMessage.tasks:
                    chatMessageData["tasks"] = chatMessage.taskToDict()

                # 保存する
                self.db \
                    .collection(DatabaseConfig.USERS_COLLECTION_NAME).document(userId) \
                    .collection(DatabaseConfig.GOALS_COLLECTION_NAME).document(goalId) \
                    .collection(DatabaseConfig.CHAT_HISTORY_COLLECTION_NAME).add(chatMessageData)
                logger.info("Saved chat message to users collect")
        except Exception as e:
            logger.error(f"Failed to save chat message: {e}", exc_info=True)
            raise  # 呼び出し元で例外をハンドリングできるように再送出

    def findByGoalIdForUser(self, userId: str, goalId: str) -> List[ChatMessage]:
        """
        チャット履歴を取得する

        Args:
            limit: 取得する履歴の最大数

        Returns:
            チャット履歴のリスト
        """
        try:
            # チャット履歴を取得する
            docs = self.db \
                .collection(DatabaseConfig.USERS_COLLECTION_NAME).document(userId) \
                .collection(DatabaseConfig.GOALS_COLLECTION_NAME).document(goalId) \
                .collection(DatabaseConfig.CHAT_HISTORY_COLLECTION_NAME) \
                .get()

            # 取得したデータをドメインモデルに変換する
            messages = []
            for doc in docs:
                data = doc.to_dict()
                try:
                    message_data = {
                        "role": data.get("role"),
                        "content": data.get("content"),
                        "createdAt": datetime.fromisoformat(data.get("created_at")),
                        "status": data.get("status"),
                    }
                    # タスクがある場合はタスクを追加
                    if data.get("tasks"):
                        taskCollection = TaskCollection()
                        for task_dict in data.get("tasks"):
                            task = Task(
                                title=task_dict["title"],
                                description=task_dict["description"],
                                deadline=datetime.strptime(task_dict["deadline"], "%Y-%m-%d").date(),
                                requiredTime=int(task_dict["requiredTime"]),
                                priority=int(task_dict["priority"]),
                            )
                            taskCollection.add(task)
                        message_data["tasks"] = taskCollection.toDict()
                    messages.append(ChatMessage(**message_data))
                except Exception as e:
                    logger.warning(f"Invalid chat message format: {e}")
            return messages

        except Exception as e:
            logger.error(f"Failed to retrieve chat history: {e}", exc_info=True)
            raise
