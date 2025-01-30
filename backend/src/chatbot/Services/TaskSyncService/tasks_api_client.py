# chatbot/services/tasks_api_client.py

import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from datetime import datetime

TASKS_SCOPES = ["https://www.googleapis.com/auth/tasks"]


def list_task_lists(service):
    """
    Google Tasks APIからタスクリストの一覧を取得する。

    :param service: Google Tasks APIのサービスオブジェクト
    :return: タスクリストのリスト [{ 'id': '...', 'title': '...' }, ...]
    """
    results = service.tasklists().list(maxResults=10).execute()
    tasklists = results.get('items', [])
    return tasklists

def get_tasks_service():
    """
    Google Tasks APIのServiceインスタンスを返す。
    認証情報が保存されていれば再利用し、なければ新たに認証フローを実行する。
    """
    creds = None
    token_path = "credentials/token_tasks.json"  # 認証結果(トークン)を保存するファイル

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, TASKS_SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials/credentials_desktop.json",  # ダウンロードしたOAuthクレデンシャルファイル
                TASKS_SCOPES
            )
            creds = flow.run_local_server(port=0)  # GUI環境がある場合
            # ヘッドレス環境の場合は flow.run_console() に変更
        # 認証した資格情報をファイルに保存 → 次回から再利用
        with open(token_path, "w") as token:
            token.write(creds.to_json())

    service = build("tasks", "v1", credentials=creds)
    return service

def create_task_list(service, title):
    """
    新しいタスクリストを作成する関数。

    :param service: Google Tasks APIのサービスオブジェクト
    :param title: タスクリストのタイトル
    :return: 作成されたタスクリストの情報
    """
    task_list = {
        "title": title
    }
    result = service.tasklists().insert(body=task_list).execute()
    return result

def create_todo_in_google_tasks(service, task_list_id, title, notes=None, due=None, parent=None):
    """
    Google TasksにTODOを作成する関数。必要に応じてサブタスクとして作成。

    :param service: Google Tasks APIのサービスオブジェクト
    :param task_list_id: タスクリストのID
    :param title: TODOのタイトル
    :param notes: TODOの詳細情報（オプション）
    :param due: TODOの期限（datetime.datetime オブジェクト、オプション）
    :param parent: 親タスクのID（サブタスクとして作成する場合に指定）
    :return: 作成されたタスクの情報
    """
    task = {
        "title": title,
        "notes": notes,
        "due": due.isoformat() + 'Z' if due else None,  # RFC3339形式
    }
    result = service.tasks().insert(tasklist=task_list_id, body=task).execute()

    if parent:
        service.tasks().move(tasklist=task_list_id, task=result["id"], parent=parent).execute()

    return result