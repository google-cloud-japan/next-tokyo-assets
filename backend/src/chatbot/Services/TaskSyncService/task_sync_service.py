# task_sync_service.py （例）
from datetime import datetime, date, timedelta, time
from .day_slot_calculator import get_day_slot_map
from .urgency_calculator import calculate_urgencies
from .daily_allocation import allocate_tasks_day_by_day
from .tasks_api_client import get_tasks_service, create_task_list, create_todo_in_google_tasks

class TaskSyncService:

    def __init__(self):
        # 必要に応じて初期化
        self.tasks_service = get_tasks_service()
        self.task_title = "AI hackathon Tasks"
        self.start_dt = date.today()
        self.end_dt = self.start_date + timedelta(days=7)

    def sync_tasks(self, tasks: list[dict]):
        """
        受け取ったタスクを、Googleカレンダーの空き状況などを考慮して
        Google Tasks(API)に同期する一連の処理をまとめる。
        """
        # 1. カレンダーから日毎スロット取得
        day_slots_map = get_day_slot_map(self.start_dt, self.end_dt)

        # 2. 割り当て計算
        updated_tasks, allocated_slots = allocate_tasks_day_by_day(
            tasks=tasks,
            day_slots_map=day_slots_map,
            start_date=self.start_dt.date(),
            end_date=self.end_dt.date()
        )

        # 3. Google Tasks APIでタスクリスト作成
        new_task_list = create_task_list(self.tasks_service, self.task_title)
        task_list_id = new_task_list['id']

        # 4. allocated_slots をもとにTODO書き込み
        for day, tasks_info in allocated_slots.items():
            for task_title, allocated_slot_num in tasks_info.items():
                if allocated_slot_num <= 0:
                    continue

                # 親タスクのタイトルとメモを設定
                parent_title = f"{task_title} (Allocated {allocated_slot_num} slots)"
                parent_notes = f"Allocated {allocated_slot_num} slots on {day}"
                
                # 親タスクの期限を設定
                due_datetime = datetime.combine(day, time(17, 0))  # 17:00に設定
                
                try:
                    # 親タスクを作成
                    parent_task = create_todo_in_google_tasks(
                        service=self.tasks_service,
                        task_list_id=task_list_id,
                        title=parent_title,
                        notes=parent_notes,
                        due=due_datetime
                    )
                    print(f"Created Parent Task: {parent_task['title']} due on {parent_task.get('due', 'N/A')}")
                    
                    # サブタスクを作成
                    for slot in range(1, allocated_slot_num + 1):
                        subtask_title = f"{task_title} - 1h"
                        subtask_notes = f"Slot {slot} of {allocated_slot_num} allocated on {day}"
                        
                        # サブタスクの期限を設定（親タスクと同じ）
                        try:
                            subtask = create_todo_in_google_tasks(
                                service=self.tasks_service,
                                task_list_id=task_list_id,
                                title=subtask_title,
                                notes=subtask_notes,
                                due=due_datetime,
                                parent=parent_task['id'],  # 親タスクのIDを指定
                            )
                            print(f"  Created Subtask: {subtask['title']} due on {subtask.get('due', 'N/A')}")
                        except Exception as e:
                            print(f"  Failed to create subtask '{subtask_title}' on {day}: {e}")
                
                except Exception as e:
                    print(f"Failed to create parent task '{parent_title}' on {day}: {e}")

        
        # 必要に応じて戻り値を返す
        return {
            "updatedTasks": updated_tasks,
            "allocatedSlots": allocated_slots,
            "taskListId": task_list_id
        }