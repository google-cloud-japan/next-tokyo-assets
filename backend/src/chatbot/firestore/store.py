from google.cloud import firestore
from datetime import datetime

def save_chat_response(response_data: dict) -> None:
    """
    generate_response の結果を Firestore に保存する

    Args:
        response_data: generate_response から返される辞書
        {
            "status": "success/error",
            "response": "生成されたレスポンステキスト",
            "prompt": "入力されたプロンプト"
        }
    """
    # Firestore クライアントの初期化
    db = firestore.Client()

    # 保存するデータを作成
    chat_doc = {
        "status": response_data["status"],
        "response": response_data["response"],
        "prompt": response_data["prompt"],
        "timestamp": firestore.SERVER_TIMESTAMP
    }

    # chat_responses コレクションに保存
    db.collection('chat_responses').add(chat_doc)