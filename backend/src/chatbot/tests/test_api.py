import requests
import json

def test_chat_api():
    """
    /chat エンドポイントのAPIテスト

    このテストでは、/chat エンドポイントが正常に動作し、
    適切なレスポンスを返すことを検証します。
    具体的なテストケースとして、日常的な質問や相談を想定したプロンプトを使用しています。
    """
    url = "http://localhost:8080/chat"
    headers = {
        "Content-Type": "application/json"
    }

    # テストケース: 様々なプロンプトと空のチャット履歴
    # 現状、チャット履歴は空で固定とし、プロンプトに対する応答を検証する
    test_cases = [
        {
            "prompt": "英語の勉強をしたいです。TOEICで800点を取ることが目標です。",
            "chat_history": []
        },
        {
            "prompt": "プログラミングスキルを向上させたい。3ヶ月でPythonを使って機械学習プロジェクトができるようになりたいです。",
            "chat_history": []
        }
    ]

    # 各テストケースについてAPIリクエストを送信し、レスポンスを確認する
    for test_case in test_cases:
        print(f"\nテストケース: {test_case['prompt']}")
        try:
            # /chat エンドポイントにPOSTリクエストを送信
            response = requests.post(url, json=test_case)
            # レスポンスステータスコードを出力
            print(f"ステータスコード: {response.status_code}")
            # レスポンス内容をJSON形式で整形して出力 (日本語文字化け対策で ensure_ascii=False を指定)
            print("レスポンス:")
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        except Exception as e:
            # エラーが発生した場合、エラー内容を出力
            print(f"エラー: {str(e)}")

if __name__ == "__main__":
    test_chat_api()