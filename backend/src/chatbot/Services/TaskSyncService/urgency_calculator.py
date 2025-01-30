import json
from datetime import datetime, date

def load_tasks_from_json(json_path: str):
    with open(json_path, "r") as f:
        return json.load(f)[0].get("tasks", [])
    
def calculate_urgencies(tasks: list[dict], current_date: date):
    for task in tasks:
        deadline_str = task.get("deadline")
        required_time_str = task.get("requiredTime", "0")

        # deadline をパース
        if deadline_str:
            deadline_date = datetime.strptime(deadline_str, "%Y-%m-%d").date()
            days_left = (deadline_date - current_date).days
        else:
            days_left = 0  # deadlineが無い場合は0とする（or None扱いでもOK）

        # requiredTimeを数値化
        try:
            required_time = float(required_time_str)
        except ValueError:
            required_time = 0.0

        # 緊急度を計算
        # days_left <= 0 の場合は期限切れ or 当日のため∞扱いや0扱いなど、要件に応じて
        if days_left <= 0:
            urgency = float('inf')  # 期限切れなど最優先
        else:
            urgency = required_time / days_left

        # 結果をtaskに格納
        task["urgency"] = urgency
