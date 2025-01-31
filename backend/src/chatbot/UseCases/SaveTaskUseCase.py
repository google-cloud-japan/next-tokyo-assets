import logging
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from Domain.Models.Task import Task
from Domain.Models.TaskCollection import TaskCollection
from Repositories.TaskRepository import TaskRepository

logger = logging.getLogger(__name__)

class SaveTaskUseCase:
    """タスク保存に関するユースケースを担当するクラス"""

    @dataclass
    class Input:

        tasks: List[dict]  # タスク一覧
        userId: str  # ユーザーID Firebase Auth ID
        goalId: str  # 目標ID

    @dataclass
    class Output:

        success: bool  # 処理の成否
        message: str  # ユーザーに表示するメッセージ
        errorMessage: Optional[str] = None  # エラーメッセージ（エラー時のみ存在）

    def __init__(self,taskRepository: TaskRepository):
        self.taskRepository = taskRepository

    def save(self, input: Input) -> Output:
        """
        LLMが生成したタスクに対してユーザが納得した場合は、そのタスクを保存する

        Args:
            input (Input): タスク保存リクエスト
        """
        # # タスクを保存する
        # taskCollection = TaskCollection()
        # logger.info(f"input.tasks: {input.tasks}")
        # # dict型のタスクをTaskCollectionに変換する
        # taskCollection = self._convertDictToTaskCollection(input.tasks)
        # self.taskRepository.add(tasks=taskCollection, userId=input.userId, goalId=input.goalId)
        
        # TODO GoogleCalenderのTODOにタスクを追加する

        return self.Output(success=True, message="タスクを保存しました")

    def _convertDictToTaskCollection(self, tasksJson: List[dict]) -> TaskCollection:
        taskCollection = TaskCollection()
        for task_dict in tasksJson:
            task = Task(
                title=task_dict["title"],
                description=task_dict["description"],
                deadline=task_dict["deadline"],
                requiredTime=int(task_dict["requiredTime"]),
                priority=int(task_dict["priority"]),
            )
            taskCollection.add(task)
        return taskCollection
