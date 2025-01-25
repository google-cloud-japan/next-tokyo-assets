# Chatbot API

タスク設計のためのチャットボットAPIです。Vertex AI（Gemini Pro）を利用して、ユーザーの目標を具体的なタスクに分解します。

## 必要条件

- Docker
- Docker Compose
- Google Cloud SDK
- Python 3.11以上（ローカルテスト用）

## セットアップ手順

### 1. Google Cloud の設定

```bash
# Google Cloud SDK のインストール（まだの場合）
brew install google-cloud-sdk

# Google Cloud にログイン
gcloud auth login

# プロジェクトの設定
gcloud config set project ai-hackathon-test1

# アプリケーションデフォルト認証情報の設定
gcloud auth application-default login
```

### 2. 必要なAPIの有効化

以下のAPIを有効化してください：
1. [Vertex AI API](https://console.cloud.google.com/apis/library/aiplatform.googleapis.com)
2. [Cloud Firestore API](https://console.cloud.google.com/apis/library/firestore.googleapis.com)

### 3. 環境変数の設定

`.env`ファイルをプロジェクトルートに作成：
```bash
cd /taskTrail/backend/src/chatbot
cp .env.example .env
```

.envの自身のプロジェクトIDに差し替えてください。
※共通のプロジェクトIDなので、現状はexampleの値は固定にしてます
他のは必要に応じて変更してください。

### 4. アプリケーションの起動

```bash
# Dockerイメージのビルドと起動
docker compose up --build
```

アプリケーションは http://localhost:8080 で利用可能になります。

## API使用方法

### チャットエンドポイント

```bash
# curlを使用する場合
curl -X POST "http://localhost:8080/chat" \
-H "Content-Type: application/json" \
-d '{
  "prompt": "英語の勉強をしたいです。TOEICで800点を取ることが目標です。",
  "chat_history": []
}'
```

### APIドキュメント

- Swagger UI: http://localhost:8080/docs
- ReDoc: http://localhost:8080/redoc

## テスト
test_apiは期待するレスポンスが返ってくるかをテストする。
test_firestoreはfirestoreに保存・削除ができるかなどの疎通確認用
```bash
# テストスクリプトの実行
docker compose exec chatbot python tests/test_api.py
docker compose exec chatbot python tests/test_firestore.py
```

## トラブルシューティング

### サービスアカウントの発行
Firebase Consoleから新しいサービスアカウントキーを取得する必要があります

- Firebase Console → プロジェクト設定 → サービスアカウント
- 「新しい秘密鍵の生成」をクリック
- ダウンロードしたJSONファイルをcredentials.jsonとして保存
- /taskTrail/backend/src/chatbot/credentials.jsonにファイルを置く

### 認証関連のエラー

1. アプリケーションデフォルト認証情報が正しく設定されているか確認
```bash
gcloud auth application-default print-access-token
```

2. 必要に応じて再設定
```bash
gcloud auth application-default login
```

## 開発ガイドライン

- コードの変更は自動的にリロードされます（`--reload`フラグ有効）
- ログは`docker compose logs -f`で確認できます