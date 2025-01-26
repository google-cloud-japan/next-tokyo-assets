from dataclasses import dataclass
from datetime import date
from typing import Dict


@dataclass
class Task:
    """タスクを表すドメインモデル"""
    title: str
    description: str
    deadline: date
    requiredTime: int
    priority: int

    def __post_init__(self):
        """バリデーションを行う"""
        if not self.title:
            raise ValueError("タイトルは必須です")
        if not self.description:
            raise ValueError("説明は必須です")
        if not isinstance(self.deadline, date):
            raise ValueError("期限は日付型である必要があります")
        if self.requiredTime <= 0:
            raise ValueError("所要時間は0より大きい必要があります")
        if not 1 <= self.priority <= 5:
            raise ValueError("優先度は1から5の間である必要があります")

    def toDict(self) -> Dict:
        """タスクを辞書形式に変換する"""
        return {
            "title": self.title,
            "description": self.description,
            "deadline": self.deadline.isoformat(),
            "requiredTime": self.requiredTime,
            "priority": self.priority,
        }

    @classmethod
    def fromDict(cls, data: Dict) -> "Task":
        """辞書形式のデータからTaskオブジェクトを生成する"""
        return cls(
            title=data["title"],
            description=data["description"],
            deadline=date.fromisoformat(data["deadline"]),
            requiredTime=int(data["requiredTime"]),
            priority=int(data["priority"]),
        )
