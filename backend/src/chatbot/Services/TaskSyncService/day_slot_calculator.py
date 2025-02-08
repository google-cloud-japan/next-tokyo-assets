from datetime import datetime, timedelta, time
import dateutil.parser  # pip install python-dateutil
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# カレンダーAPIのスコープ: 読み取り専用にする場合
CALENDAR_SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

def get_calendar_service(access_token):
    """
    GoogleカレンダーAPIのServiceインスタンスを返す。
    ローカルPCなどで実行し、ブラウザ認証することを想定。
    """
    creds = Credentials(
        token=access_token,
        # refresh_token=None,
        # token_uri="https://oauth2.googleapis.com/token",
        # client_id=client_id,
        # client_secret=client_secret,
        scopes=["https://www.googleapis.com/auth/calendar"]
    )
    service = build("calendar", "v3", credentials=creds)
    return service

def get_daily_booked_hours(service, calendar_id, start_date, end_date):
    """
    指定期間内のイベントを取得し、日毎の合計ブッキング時間(時間単位)を返す。
    
    :param service: Google Calendar APIのservice
    :param calendar_id: カレンダーID (例: "primary")
    :param start_date: 取得開始日時 (datetime)
    :param end_date: 取得終了日時 (datetime)
    :return: { date: float(ブッキング時間) } の辞書 (dateはdatetime.date)
    """
    
    dt_start = datetime.combine(start_date, time.min)  # 00:00:00
    dt_end   = datetime.combine(end_date,   time.min)  # 同様に 00:00:00
    timeMin=dt_start.isoformat() + "Z"  # ISO8601, UTC形式
    timeMax=dt_end.isoformat() + "Z"    # end_date自体を含めたければ+1日するなど

    # イベント取得
    events_result = service.events().list(
        calendarId=calendar_id,
        timeMin=timeMin,
        timeMax=timeMax,
        singleEvents=True,
        orderBy="startTime"
    ).execute()

    events = events_result.get("items", [])

    # 日毎に合計するための辞書
    day_booked = {}

    # 期間中の日を0で初期化 (あくまで「枠」を作る)
    temp_day = start_date
    while temp_day < end_date:
        day_booked[temp_day] = 0.0
        temp_day += timedelta(days=1)

    for event in events:
        start_str = event.get("start", {}).get("dateTime")
        end_str = event.get("end", {}).get("dateTime")
        
        # 全日イベント(date)の場合の処理
        if not start_str:
            # "date" フィールドがあるか確認
            start_str = event.get("start", {}).get("date")
            end_str = event.get("end", {}).get("date")
            if start_str and end_str:
                # 全日イベントの期間を日にちごとに加算するなど、ルールに応じて処理
                # ここでは簡易的に「全日=8時間」として1日ずつ加算する例
                start_dt = dateutil.parser.isoparse(start_str)
                end_dt = dateutil.parser.isoparse(end_str)
                current = start_dt
                while current < end_dt:
                    d = current.date()
                    if d in day_booked:
                        day_booked[d] += 8.0  # 全日分を加算(仮)
                    current += timedelta(days=1)
            continue

        # 通常の「dateTime」
        start_dt = dateutil.parser.isoparse(start_str)
        end_dt = dateutil.parser.isoparse(end_str)

        event_date = start_dt.date()
        duration = (end_dt - start_dt).total_seconds() / 3600.0  # 時間に変換
        if event_date in day_booked:
            day_booked[event_date] += duration
        else:
            # 期間外の日付にかかっているイベントなどの場合
            pass

    return day_booked

def decide_num_tasks(booked_hours):
    """
    占有時間(booked_hours)に応じて、割り当てるタスク数を決定する。
    例: 2h未満→5タスク, 2~4h→4タスク, 4~6h→3, 6h以上→2タスクなど
    """
    if booked_hours < 2:
        return 5
    elif booked_hours < 4:
        return 4
    elif booked_hours < 6:
        return 3
    else:
        return 1
    
def get_day_slot_map(start_date, end_date, access_token):
    cal_service = get_calendar_service(access_token)
    calendar_id = "primary"
    day_booked_map = get_daily_booked_hours(cal_service, calendar_id, start_date, end_date)

    allocation_result = {}
    for day, hours in sorted(day_booked_map.items()):
        num_tasks = decide_num_tasks(hours)
        allocation_result[day] = num_tasks

    return allocation_result

def main(access_token):
    # 1) カレンダーAPIサービスの初期化
    cal_service = get_calendar_service(access_token)

    # 2) 取得したい期間を設定
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    end = today + timedelta(days=7)  # 例: 1週間分

    # 3) 日毎の予定(イベント)合計時間を取得
    calendar_id = "primary"  # or 他のカレンダーID
    day_booked_map = get_daily_booked_hours(cal_service, calendar_id, today, end)

    # 4) 日毎のタスク割り当て数を決定
    allocation_result = {}
    for day, hours in sorted(day_booked_map.items()):
        num_tasks = decide_num_tasks(hours)
        allocation_result[day] = num_tasks

    # 5) 結果を表示
    for day, tasks_count in allocation_result.items():
        print(f"{day}: Booked={day_booked_map[day]:.1f}h, Allocate {tasks_count} tasks")

if __name__ == "__main__":
    main()