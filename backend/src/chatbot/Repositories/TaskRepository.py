import logging
from datetime import datetime

from Config.DatabaseConfig import DatabaseConfig
from Domain.Models.TaskCollection import TaskCollection
from Infrastructure.Firebase.FirebaseClient import FirebaseClient

logger = logging.getLogger(__name__)


class TaskRepository:
    """
    Firestoreを使用したタスクの永続化を担当するクラス
    タスクは目標を達成するためのものなので、Goalsの子コレクションとして保存する
    """
    def __init__(self):
        self._firebase = FirebaseClient.get_instance()
        self._db = self._firebase.db
        logger.info("TaskRepository initialized with FirebaseClient")

    def add(self, tasks: TaskCollection, userId: str, goalId: str) -> None:
        """
        タスクを保存する

        Args:
            tasks (TaskCollection): タスク一覧
            userId (str): ユーザーID Firebase Auth ID
            goalId (str): 目標ID
        """
        try:
            logger.info(f"Saving tasks to goals collection: {tasks.toDict()}")
            # タスクの一覧をGoalsの子コレクションとして保存する
            tasks_ref = self._db \
                .collection(DatabaseConfig.USERS_COLLECTION_NAME).document(userId) \
                .collection(DatabaseConfig.GOALS_COLLECTION_NAME).document(goalId) \
                .collection(DatabaseConfig.TASKS_COLLECTION_NAME)
            """
             FireStoreのバッチ書き込みを開始
             バッチ書き込みは、複数のFireStore操作をまとめてアトミックに実行するための仕組み
             ここでは、複数のタスクを一度にFireStoreに書き込むために使用しています。
             これにより、個別に書き込むよりも効率的に処理を行うことができ、
             全てのタスクが保存されるか、全く保存されないかの原子性を保証できます。
            """
            batch = self._db.batch()
            for task_dict in tasks.toDict():
                task_ref = tasks_ref.document()
                batch.set(task_ref, {**task_dict, 'created_at': datetime.now()})

            # バッチ書き込みを実行 (バッチ内の全ての操作が成功するか、全てロールバックされます)
            batch.commit()
            logger.info("Saved tasks to goals collection")
        except Exception as e:
            logger.error(f"Failed to save tasks: {e}", exc_info=True)
            raise  # 呼び出し元で例外をハンドリングできるように再送出
