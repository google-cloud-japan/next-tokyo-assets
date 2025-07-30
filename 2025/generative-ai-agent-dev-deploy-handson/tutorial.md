# Generative AI Agent ハンズオンチュートリアル

このチュートリアルでは、Google Cloud を活用して、生成AIエージェントの開発、デプロイ、評価、そしてWebアプリケーションへの統合までの一連のプロセスを学びます。

## 1. はじめに

このハンズオンでは、以下のステップを体験します。

- **ローカルでのエージェント実行**: `adk` ツールキットを使い、ローカル環境でエージェントを動かします。
- **Cloud Build によるデプロイ**: エージェントをコンテナ化し、Cloud Build を使って Vertex AI Agent Engine に自動でデプロイします。
- **エージェントの評価**: `adk eval` を用いて、定義した評価セットに基づきエージェントの性能を評価します。
- **評価セットの作成**: `adk web` のUIを使って、対話的に新しい評価セットを作成します。
- **CI/CD への評価の組み込み**: Cloud Build のパイプラインに評価ステップを追加し、デプロイ前にエージェントの品質を自動でチェックする仕組みを構築します。
- **Web アプリケーションとの連携**: Python (Streamlit) で作成されたシンプルなWebアプリから、デプロイしたAgent Engineを呼び出します。
- **Web アプリケーションのデプロイ**: WebアプリをCloud Build を使って Cloud Run にデプロイします。
- **IAP によるアクセス制御**: デプロイしたCloud Runアプリに Identity-Aware Proxy (IAP) を設定し、セキュアなアクセス制御を実現します。

## 2. セットアップ

まず、作業に必要な環境をセットアップします。

### 2.1. `agents` ディレクトリのセットアップ

1.  `agents` ディレクトリに移動します。
    ```bash
    cd agents
    ```

2.  Pythonの仮想環境を作成し、必要なライブラリをインストールします。
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

### 2.2. `client` ディレクトリのセットアップ

1.  `client` ディレクトリに移動します。
    ```bash
    cd ../client
    ```

2.  同様に、Pythonの仮想環境を作成し、ライブラリをインストールします。
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

3.  ルートディレクトリに戻ります。
    ```bash
    cd ..
    ```

## 3. Hello Agent をローカルで実行 (adk web)

`adk web` を使うと、ローカルでエージェントの動作確認やデバッグが簡単に行えるWeb UIが起動します。

1.  `agents` ディレクトリに移動します。
    ```bash
    cd agents
    ```

2.  `adk web` コマンドを実行します。
    ```bash
    adk web .
    ```

3.  ブラウザで `http://localhost:8080` を開くと、チャットUIが表示されます。ここでエージェントと対話し、動作を確認できます。
    "今日の東京の天気は？" などを入力して、エージェントが `get_weather` ツールを正しく呼び出すことを確認してください。

## 4. Hello Agent を Cloud Build を使ってデプロイ

次に、`agents/cloudbuild.yaml` を使って、エージェントを Vertex AI Agent Engine にデプロイします。

1.  `agents` ディレクトリにいることを確認してください。

2.  以下のコマンドを実行して、Cloud Build をトリガーします。`[YOUR_PROJECT_ID]` はご自身のGoogle CloudプロジェクトIDに置き換えてください。
    ```bash
    gcloud builds submit . --config cloudbuild.yaml \
         --substitutions=_PROJECT_ID=[YOUR_PROJECT_ID],_REGION=us-central1,_AGENT_NAME=my-awesome-agent
    ```
    このコマンドは、`app.agent_engine_app.py` を実行し、エージェントをVertex AI Agent Engineにデプロイします。

3.  デプロイが完了すると、Google Cloudコンソールの Vertex AI > Agent Engine のページでデプロイされたエージェントが確認できます。

## 5. Evaluation をしてみる (adk eval)

`adk eval` を使うと、事前に定義された評価セット (`evalset`) を使ってエージェントのパフォーマンスを評価できます。

1.  `agents` ディレクトリにいることを確認してください。

2.  以下のコマンドを実行します。
    ```bash
    adk eval app/ app/simple_weather_eval_set.evalset.json --config_file_path=evaluations/test_config.json --print_detailed_results
    ```
    このコマンドは、`app/simple_weather_eval_set.evalset.json` に定義された対話例（"今日の東京の天気は？"など）をエージェントに実行させ、期待されるツールの呼び出しや最終的な応答がなされたかを評価します。

## 6. Eval-set を作ってみる

`adk web` のUIから、新しい評価セットを対話的に作成できます。

1.  `adk web .` が実行中であることを確認し、ブラウザでUIを開きます。
2.  エージェントと新しい対話を行います（例：「サンフランシスコの今の時間は？」）。
3.  対話が完了したら、UI上部にある「Save as Eval Case」ボタンをクリックします。
4.  Eval ID（例：`sf-time`）を入力し、既存の `simple_weather_eval_set` に追加するか、新しいEval Setを作成します。
5.  これにより、`app/simple_weather_eval_set.evalset.json` ファイルが更新され、新しい評価ケースが追加されます。

## 7. Eval を Cloud Build に組み込む

CI/CDプロセスに評価ステップを組み込むことで、コードの変更がエージェントの品質を損なっていないかを自動的に確認できます。

1.  `agents/cloudbuild.yaml` ファイルを以下のように編集し、`eval` ステップを追加します。

    ```yaml
    steps:
      - name: "python:3.12"
        id: deploy
        entrypoint: /bin/bash
        args:
          - "-c"
          - |
            pip install -r requirements.txt && python3 -m app.agent_engine_app --project ${_PROJECT_ID} --agent-name ${_AGENT_NAME} --location ${_REGION}
      
      - name: "python:3.12"
        id: eval
        entrypoint: /bin/bash
        args:
          - "-c"
          - |
            pip install -r requirements.txt
            adk eval app/ app/simple_weather_eval_set.evalset.json --config_file_path=evaluations/test_config.json
    
    substitutions:
      _PROJECT_ID: YOUR_PROJECT_ID
      _REGION: us-central1
      _AGENT_NAME: my-first-agent
    
    logsBucket: gs://${PROJECT_ID}-sample-app-logs-data/build-logs
    options:
      substitutionOption: ALLOW_LOOSE
      defaultLogsBucketBehavior: REGIONAL_USER_OWNED_BUCKET
    ```

2.  変更を保存し、再度 `gcloud builds submit` を実行すると、デプロイ後に評価が自動的に実行されるようになります。

## 8. ローカルの Python Web App から Agent Engine を叩く

`client` ディレクトリにあるStreamlit製のWebアプリケーションから、デプロイ済みのAgent Engineを呼び出します。

1.  `client/webapp.py` を開き、`agent_engines.get()` の引数を、ご自身がデプロイしたエージェントのリソース名に書き換えます。リソース名は、デプロイ時のログやGoogle Cloudコンソールから確認できます。

    ```python
    # client/webapp.py

    # ... (省略) ...
    # Agentの初期化
    # 例: "projects/your-project-id/locations/us-central1/reasoningEngines/1234567890"
    agent = agent_engines.get("[YOUR_AGENT_ENGINE_RESOURCE_NAME]") 
    # ... (省略) ...
    ```

2.  `client` ディレクトリに移動し、仮想環境を有効にしてアプリを起動します。
    ```bash
    cd ../client
    source venv/bin/activate
    streamlit run webapp.py
    ```

3.  ブラウザで表示されたWebアプリから、ユーザーIDとメッセージを入力してエージェントと対話できることを確認します。

## 9. Python Web App を Cloud Run にデプロイする

次に、このWebアプリケーションをCloud Runにデプロイします。

1.  `client` ディレクトリにいることを確認してください。

2.  以下のコマンドを実行して、Cloud Build経由でCloud Runにデプロイします。Cloud Build は、実行されているプロジェクトのIDを自動的に `PROJECT_ID` として利用します。
    ```bash
    gcloud builds submit . --config cloudbuild.yaml \
        --substitutions=_SERVICE_NAME=client-agent,_REGION=us-central1
    ```
    このコマンドは、`Dockerfile` を使ってコンテナイメージをビルドし、Cloud Runにデプロイします。


3.  デプロイが完了すると、出力に表示されるURLからWebアプリケーションにアクセスできます。

## 10. Cloud Run に IAP を設定する

最後に、デプロイしたWebアプリケーションにIAPを設定して、認証されたユーザーのみがアクセスできるようにします。

1.  **OAuth同意画面の設定**: まず、Google CloudコンソールでプロジェクトのOAuth同意画面を設定する必要があります（未設定の場合）。

2.  **IAPを有効にする**: 以下のコマンドで、Cloud Runサービスを更新してIAPを有効にします。`[SERVICE_NAME]` はCloud Runのサービス名（例: `client-agent`）、`[PROJECT_ID]` を置き換えてください。
    ```bash
    gcloud run services update [SERVICE_NAME] \
      --region=us-central1 \
      --project=[PROJECT_ID] \
      --update-labels=cloud.googleapis.com/iap-enabled=true
    ```

3.  **アクセス権限の付与**: IAP経由でのアクセスを許可したいユーザー（またはグループ、サービスアカウント）に `IAP-secured Web App User` ロールを付与します。
    ```bash
    gcloud run services add-iam-policy-binding [SERVICE_NAME] \
      --region=us-central1 \
      --project=[PROJECT_ID] \
      --member="user:[USER_EMAIL]" \
      --role="roles/iap.httpsResourceAccessor"
    ```
    `[USER_EMAIL]` にはアクセスを許可したいユーザーのメールアドレスを指定します。

これで、指定したユーザーのみがWebアプリケーションにアクセスできるようになりました。

## 11. おわりに

このチュートリアルでは、Generative AI Agentの開発からデプロイ、評価、Webアプリへの統合、そしてセキュリティ設定まで、一連のライフサイクルを体験しました。ここからさらに、エージェントの能力を拡張したり、より複雑なワークフローを構築したりすることに挑戦してみてください。
