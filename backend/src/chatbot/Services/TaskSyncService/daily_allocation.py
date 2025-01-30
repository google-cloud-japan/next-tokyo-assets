from datetime import date, datetime, timedelta, time
import math

import day_slot_calculator
import urgency_calculator
import tasks_api_client

TASK_TITLE = "AI hackathon Tasks"

def update_allocated_slots(allocated_slots, current_day, task_title, allocated_slot_num):
    """
    allocated_slots は次のような構造を想定:
      {
        date(2025,1,26): {
          "Task A": 2,
          "Task B": 1
        },
        date(2025,1,27): {
          "Task A": 3
        },
        ...
      }

    :param allocated_slots: 上記のような辞書
    :param current_day:  日付キー (例: date(2025,1,26))
    :param task_title:   タスク名の文字列
    :param allocated_slot_num: 加算したいスロット数 (float/int)

    この関数では、指定した日付・タスク名に対して
    既存の値に「allocated_slot_num」だけ加算し、
    結果を allocated_slots に反映します。
    """
    # 1) その日の辞書を取り出す (無ければ空dictを返す)
    day_dict = allocated_slots.get(current_day, {})

    # 2) 指定タスクの既存値を取り出す (無ければ 0)
    current_val = day_dict.get(task_title, 0)

    # 3) 割り当てスロット数を加算
    current_val += allocated_slot_num

    # 4) 日付内の辞書を更新
    day_dict[task_title] = current_val

    # 5) updated な日付辞書を再度挿入
    allocated_slots[current_day] = day_dict

def allocate_tasks_day_by_day(
    tasks: list[dict],
    day_slots_map: dict,  # {日付: スロット数}
    start_date: date,
    end_date: date
):
    """
    day_slots_map に従い、 start_date から end_date までの日を1日ずつ進めて
    タスクに割り当てを行う。
    
    - まず、その時点の日付(current_day)を使ってタスクの緊急度を再計算
    - day_slots_map[current_day] のスロット数を、緊急度に応じて各タスクへ割り当て
    - 割り当てられた分だけ tasks[i]["requiredTime"] を減らす
    - requiredTime が 0 以下のタスクは完了扱い(以降の割り当て対象外)
    - 次の日に進んで再度緊急度計算 → 割り当て … を繰り返す
    """
    # タスクに日別の割り当てログを持たせたい場合、task["allocatedDays"] = {} などの構造を用意
    for t in tasks:
        t["allocatedTime"] = 0  # 割り当て合計時間(またはスロット数)
        t["requiredTime"] = int(t["requiredTime"])  # 必要時間を整数に変換

    # 日別割り当てログ
    allocated_slots = {}

    current_day = start_date
    while current_day <= end_date:
        if current_day in day_slots_map:
            slots_today = day_slots_map[current_day]
        else:
            slots_today = 0
        
        # 1) 緊急度を再計算 (deadline - current_day).days
        urgency_calculator.calculate_urgencies(tasks, current_day)

        # 2) まだ完了していないタスクをフィルター
        ongoing_tasks = [t for t in tasks if int(t["requiredTime"]) > int(t["allocatedTime"])]

        if not ongoing_tasks or slots_today <= 0:
            # 割り当て可能スロットなし、または残タスクなしならスキップ
            current_day += timedelta(days=1)
            continue
        
        # 全タスクの緊急度合計
        total_urgency = sum(t["urgency"] for t in ongoing_tasks if not math.isinf(t["urgency"]))

        # 期限切れや days_left<=0 で `urgency=inf` のタスクの扱い
        infinite_urgency_tasks = [t for t in ongoing_tasks if math.isinf(t["urgency"])]

        # 3) 割り当て計算
        #    例: "1スロット=1時間" という前提で、slots_today 時間を各タスクに比例配分する
        #    (本当は more complex allocation = Hamilton法(最大剰余法) etc. が望ましいが、簡易実装に留める)
        
        # -- まず無限大(期限切れ)のタスクがあれば最優先でスロット全部割り当てる例 --
        if infinite_urgency_tasks:
            # ここでは「期限切れタスクすべてに slots_today を均等割り当て」する例
            # 実運用では「全部突っ込む」「優先度1つのタスクだけ進める」などケースによる
            while True:
                flag = False
                for itask in infinite_urgency_tasks:
                    itask["allocatedTime"] += 1
                    # ログ
                    update_allocated_slots(allocated_slots, current_day, itask["title"], 1)
                    slots_today -= 1
                    
                    if itask["requiredTime"] == itask["allocatedTime"]:
                        infinite_urgency_tasks.remove(itask)

                    if slots_today <= 0:
                        flag = True
                        break
                
                if flag or not infinite_urgency_tasks:
                    break
                
        else:
            # 通常の有限urgencyタスクでの配分
            if total_urgency <= 0:
                # すべてurgency=0の場合 or 何か例外
                # → 均等割り or とりあえずスキップなど
                current_day += timedelta(days=1)
                continue
            
            # ratio配分: (タスクのurgency / total_urgency) * slots_today
            for tsk in ongoing_tasks:
                allocated_slot_num = min(int((tsk["urgency"] / total_urgency) * slots_today), tsk["requiredTime"] - tsk["allocatedTime"])
                tsk["allocatedTime"] += allocated_slot_num

                if tsk["requiredTime"] == tsk["allocatedTime"]:
                    ongoing_tasks.remove(tsk)
                
                # ログ記録: いつ何時間（スロット）配分したか
                update_allocated_slots(allocated_slots, current_day, tsk["title"], allocated_slot_num)
                slots_today -= allocated_slot_num

            if slots_today > 0 and ongoing_tasks:
                # まだ余っている場合、緊急度が高い順に割り当てる
                ongoing_tasks.sort(key=lambda x: x["urgency"], reverse=True)
                for tsk in ongoing_tasks:
                    if slots_today <= 0:
                        break
                    tsk["allocatedTime"] += 1
                    # ログ
                    update_allocated_slots(allocated_slots, current_day, tsk["title"], 1)
                    slots_today -= 1
                    if tsk["requiredTime"] == tsk["allocatedTime"]:
                        ongoing_tasks.remove(tsk)

        # 次の日へ
        current_day += timedelta(days=1)
    
    return tasks, allocated_slots


def main():
    # スロット計算プログラムから「日毎の稼働可能なスロット数」を取得
    start_dt = datetime(2025, 1, 26)
    end_dt = datetime(2025, 1, 28)
    day_slots_map = day_slot_calculator.get_day_slot_map(start_dt, end_dt)
    
    # タスク一覧(JSON)をロード & 緊急度を最初に計算
    tasks = urgency_calculator.load_tasks_from_json("tests/input_tasks.json")
    
    updated_tasks, allocated_slots = allocate_tasks_day_by_day(
        tasks=tasks,
        day_slots_map=day_slots_map,
        start_date=start_dt.date(),
        end_date=end_dt.date()
    )
    
    # allocated_slots は {date: {task_title: allocated_slot_num}} の形式
    # 例: {date(2025,1,26): {"Task A": 2, "Task B": 1}, date(2025,1,27): {"Task A": 3}, ...}

    tasks_service = tasks_api_client.get_tasks_service()
    
    # 新しいタスクリストのタイトルを設定
    new_task_list = tasks_api_client.create_task_list(tasks_service, TASK_TITLE)
    task_list_id = new_task_list['id']
    # print(f"Created new Task List: ID={task_list_id}, Title={new_task_list['title']}")


    # 7) Tasks APIを通してTODOとして書き込む（サブタスクを作成）
    for day, tasks_info in allocated_slots.items():
        for task_title, allocated_slot_num in tasks_info.items():
            if allocated_slot_num <= 0:
                # 0スロット割り当ての場合はタスクを作成しない
                continue

            # 親タスクのタイトルとメモを設定
            parent_title = f"{task_title} (Allocated {allocated_slot_num} slots)"
            parent_notes = f"Allocated {allocated_slot_num} slots on {day}"
            
            # 親タスクの期限を設定
            due_datetime = datetime.combine(day, time(17, 0))  # 17:00に設定
            
            try:
                # 親タスクを作成
                parent_task = tasks_api_client.create_todo_in_google_tasks(
                    service=tasks_service,
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
                        subtask = tasks_api_client.create_todo_in_google_tasks(
                            service=tasks_service,
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


    print("=== Tasks have been allocated and written to Google Tasks ===")



if __name__ == "__main__":
    main()