from datetime import datetime
from enum import Enum
from typing import List, Optional

from Domain.Models.TaskCollection import TaskCollection


class ChatRole(str, Enum):
    """チャットメッセージの送信者役割を定義する列挙型"""

    USER = "user"  # ユーザーからのメッセージ
    ASSISTANT = "assistant"  # アシスタントからのメッセージ


class ChatStatus(str, Enum):
    """チャットメッセージの状態を定義する列挙型"""

    ACTIVE = "active"  # アクティブ
    ARCHIVED = "archived"  # アーカイブ済み


class ChatMessage:
    """チャットメッセージを表すドメインモデル"""

    def __init__(
        self,
        role: ChatRole,
        content: str,
        createdAt: datetime = datetime.now(),
        status: ChatStatus = ChatStatus.ACTIVE,
        tasks: Optional[TaskCollection] = None,  # TaskCollectionとしてタスクを保存
    ):
        if not content:
            raise ValueError("Chat content cannot be empty")

        self._role = role
        self._content = content
        self._createdAt = createdAt
        self._status = status
        self._tasks = tasks

    @property
    def role(self) -> ChatRole:
        return self._role

    @property
    def content(self) -> str:
        return self._content

    @property
    def createdAt(self) -> datetime:
        return self._createdAt

    @property
    def status(self) -> ChatStatus:
        return self._status

    @property
    def tasks(self) -> Optional[str]:
        return self._tasks

    def taskToDict(self) -> Optional[List[dict]]:
        return self._tasks.toDict() if self._tasks else []

    def archive(self):
        """メッセージをアーカイブ状態に変更（論理削除）"""
        self._status = ChatStatus.ARCHIVED

    @property
    def is_active(self) -> bool:
        """メッセージがアクティブ状態かどうかを返す"""
        return self._status == ChatStatus.ACTIVE
