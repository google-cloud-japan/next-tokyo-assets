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

def get_tasks_service(access_token):
    """
    Google Tasks APIのServiceインスタンスを返す。
    認証情報が保存されていれば再利用し、なければ新たに認証フローを実行する。
    """
    creds = Credentials(
        token=access_token,
        # refresh_token=refresh_token,
        # token_uri="https://oauth2.googleapis.com/token",  # Google OAuthのトークンエンドポイント
        # client_id=client_id,
        # client_secret=client_secret,
        scopes=TASKS_SCOPES
    )
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