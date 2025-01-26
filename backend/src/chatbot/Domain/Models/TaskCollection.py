import json
from typing import Dict, List, Optional

from Domain.Models.Task import Task


class TaskCollection:
    """タスクのコレクションを表すドメインモデル"""

    def __init__(self, tasks: Optional[List[Task]] = None):
        self._tasks = tasks or []

    def add(self, task: Task) -> None:
        """タスクを追加する"""
        self._tasks.append(task)

    def remove(self, task: Task) -> None:
        """タスクを削除する"""
        self._tasks.remove(task)

    def clear(self) -> None:
        """全タスクを削除する"""
        self._tasks.clear()

    @property
    def tasks(self) -> List[Task]:
        """タスクのリストを取得する"""
        return self._tasks

    def toDict(self) -> List[Dict]:
        """タスクコレクションを辞書形式に変換する"""
        return [task.toDict() for task in self._tasks]

    def toJson(self) -> str:
        """タスクコレクションをJSON文字列に変換する"""
        return json.dumps(self.toDict(), ensure_ascii=False, indent=2)

    @classmethod
    def fromDict(cls, data: List[Dict]) -> "TaskCollection":
        """辞書形式のデータからTaskCollectionオブジェクトを生成する"""
        tasks = [Task.fromDict(task_dict) for task_dict in data]
        return cls(tasks)

    @classmethod
    def fromJson(cls, json_str: str) -> "TaskCollection":
        """JSON文字列からTaskCollectionオブジェクトを生成する"""
        data = json.loads(json_str)
        return cls.fromDict(data)

    def __len__(self) -> int:
        return len(self._tasks)

    def __iter__(self):
        return iter(self._tasks)

    def __getitem__(self, index: int) -> Task:
        return self._tasks[index] 