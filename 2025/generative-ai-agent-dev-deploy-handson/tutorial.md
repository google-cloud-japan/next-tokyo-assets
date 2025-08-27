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

### 2.1. Google Cloud プロジェクトの設定

gcloud コマンドラインツールが正しいプロジェクトを指していることを確認します。
`YOUR_PROJECT_ID` をご自身のプロジェクトIDに置き換えて実行してください。

```bash
gcloud config set project YOUR_PROJECT_ID
```

### 2.2. Google Cloud APIの有効化

このハンズオンで利用する各種Google Cloud APIを有効にします。

```bash
gcloud services enable \
  aiplatform.googleapis.com \
  cloudbuild.googleapis.com \
  run.googleapis.com \
  storage.googleapis.com \
  containerregistry.googleapis.com \
  iap.googleapis.com \
  cloudresourcemanager.googleapis.com
```


### 2.3. `uv` のインストール (初回のみ)

このチュートリアルでは、高速なPythonパッケージインストーラー `uv` を使用します。もし未インストールであれば、以下のコマンドを実行してください。

```bash
pip install uv
```

### 2.4. `agents` ディレクトリのセットアップ

1.  `agents` ディレクトリに移動します。
    ```bash
    cd agents
    ```

2.  `uv` を使ってPythonの仮想環境を作成し、必要なライブラリをインストールします。
    ```bash
    uv venv venv
    source venv/bin/activate
    uv pip install -r requirements.txt
    ```
    これで、エージェント開発用の環境が整いました。

## 3. Hello Agent をローカルで実行 (adk web)

`adk web` を使うと、ローカルでエージェントの動作確認やデバッグが簡単に行えるWeb UIが起動します。

1.  `agents` ディレクトリにいること、そして仮想環境が有効になっていることを確認してください。

2.  `adk web` コマンドを実行します。
    ```bash
    adk web .
    ```

3.  Cloud Shellで実行している場合、コマンド実行後に表示されるWebプレビューのURLを `Ctrl` (Macの場合は `Cmd`) を押しながらクリックしてUIを開きます。ローカル環境の場合は、ブラウザで `http://localhost:8080` を開きます。
    UIが表示されたら、左上のプルダウンメニューから `app` を選択します。
    チャットUIが表示されますので、ここでエージェントと対話し、動作を確認できます。
    "今日の東京の天気は？" などを入力して、エージェントが `get_weather` ツールを正しく呼び出すことを確認してください。
    このUIは、エージェントの動作をリアルタイムで確認するのに非常に便利です。

動作確認が終わったら、ターミナルで `Ctrl+C` を押して `adk web` プロセスを停止してください。

## 4. Hello Agent を Cloud Build を使ってデプロイ

次に、`agents/cloudbuild.yaml` を使って、エージェントを Vertex AI Agent Engine にデプロイします。

1.  `agents` ディレクトリにいることを確認してください。

2.  以下のコマンドを実行して、Cloud Build をトリガーします。
    ```bash
    gcloud builds submit . --config cloudbuild.yaml \
         --substitutions=_REGION=us-central1,_AGENT_NAME=my-awesome-agent
    ```
    このコマンドは、`app.agent_engine_app.py` を実行し、エージェントをVertex AI Agent Engineにデプロイします。
    **実行には数分かかります。** 待ち時間の間、デプロイされるエージェントの実装 (`agents/app/agent.py`) や、デプロイ処理を定義しているスクリプト (`agents/app/agent_engine_app.py`) の中身を確認してみましょう。

3.  デプロイが完了すると、Google Cloudコンソールの Vertex AI > Agent Engine のページでデプロイされたエージェントが確認できます。
    これで、あなたのエージェントがクラウド上で稼働を開始しました。



## 5. Evaluation をしてみる (adk eval)

`adk eval` を使うと、事前に定義された評価セット (`evalset`) を使ってエージェントのパフォーマンスを評価できます。

1.  `agents` ディレクトリにいることを確認してください。

2.  以下のコマンドを実行します。
    ```bash
    adk eval app/ app/simple_weather_eval_set.evalset.json --config_file_path=evaluations/test_config.json --print_detailed_results
    ```
    このコマンドは、`app/simple_weather_eval_set.evalset.json` に定義された対話例（"今日の東京の天気は？"など）をエージェントに実行させ、期待されるツールの呼び出しや最終的な応答がなされたかを評価します。
    評価結果を確認し、エージェントが期待通りに動作しているかを確認しましょう。

> **【重要】ツールのDocstringと評価（Eval）の関係**
>
> `adk eval` が正しく動作するためには、エージェントが利用するツール（この例では `get_weather`）の **docstring** が非常に重要です。
> LLMはdocstringを読んで、ツールをどのように呼び出すべきか（特に引数 `query` に何を入れるべきか）を判断します。
>
> `agents/app/agent.py` の `get_weather` 関数のdocstringには、`query` 引数の説明に `例: [Tokyo, New York]` という**具体例**が書かれています。
> この具体例があるおかげで、LLMは「"今日の東京の天気は？"」という日本語の質問から、`query` には `"Tokyo"` という英語の地名だけを渡すべきだと正しく推論できます。
>
> もしこの具体例が書かれていないと、LLMが `query` に `"今日の東京の天気は？"` という文章全体を渡してしまったり、`"東京"` という日本語を渡してしまったりする可能性があります。その結果、ツールが期待通りに動作せず、評価がエラーになることがあります。
> ツールを定義する際は、LLMが正しく引数を渡せるように、docstringに具体例を記述することを心がけてください。

## 6. Eval-set を作ってみる

`adk web` のUIを使い、対話的に新しい評価ケースを作成し、既存の評価セットに追加します。

1.  まず、`adk web` を再度起動します。
    ```bash
    adk web .
    ```
2.  Cloud ShellまたはブラウザでUIを開き、左上のプルダウンメニューから `app` を選択します。
3.  エージェントと新しい対話を行います（例：「サンフランシスコの今の天気は？」）。
4.  対話が完了したら、画面上部の **`Evals`** タブに移動します。
5.  左側の `Eval Sets` パネルから **`simple_weather_eval_set`** を選択します。
6.  **`Save Last Chat as Eval Case`** ボタンをクリックします。
7.  `Eval ID` に `sf-time` のような一意のIDを入力し、`Save` ボタンをクリックします。
8.  `app/simple_weather_eval_set.evalset.json` ファイルが更新され、新しい評価ケースが追加されたことを確認できます。
9.  UI上で **`Run Evaluation`** ボタンをクリックすると、更新された評価セットで即座に評価を実行できます。結果が画面に表示されることを確認してください。

評価セットの作成と実行が完了したら、ターミナルで `Ctrl+C` を押して `adk web` プロセスを停止してください。

## 7. Eval を Cloud Build に組み込む

CI/CDプロセスに評価ステップを組み込むことで、コードの変更がエージェントの品質を損なっていないかを自動的に確認できます。

1.  `agents/cloudbuild.yaml` ファイルを以下のように編集し、`eval` ステップを追加します。

    ```yaml
    steps:
      # Step 1: 依存関係をワークスペース内の仮想環境にインストールする
      - name: "python:3.12"
        id: install-dependencies
        entrypoint: /bin/bash
        args:
          - "-c"
          - |
            python3 -m venv /workspace/.venv
            . /workspace/.venv/bin/activate
            pip install uv
            uv pip install -r requirements.txt
    
      # Step 2: 評価を実行する
      # 仮想環境をアクティベートしてから評価スクリプトを実行します。
      - name: "python:3.12"
        id: eval
        waitFor: ['install-dependencies']
        entrypoint: /bin/bash
        env:
          - 'PYTHONPATH=.'
        args:
          - "-c"
          - |
            source /workspace/.venv/bin/activate
            adk eval app/ app/simple_weather_eval_set.evalset.json --config_file_path=evaluations/test_config.json | tee eval_output.log
            # grepで"Tests failed"に0以外の数字が続く行があるかチェックし、あればビルドを失敗させます
            if grep -q "Tests failed: [1-9][0-9]*" eval_output.log; then
              echo "Evaluation failed."
              exit 1
            fi
    
      # Step 3: 評価が成功した場合のみデプロイを実行する
      # 仮想環境をアクティベートしてからデプロイスクリプトを実行します。
      - name: "python:3.12"
        id: deploy
        waitFor: ['eval']
        entrypoint: /bin/bash
        env:
          - 'PYTHONPATH=.'
        args:
          - "-c"
          - |
            source /workspace/.venv/bin/activate
            python3 -m app.agent_engine_app \
              --project ${PROJECT_ID} \
              --agent-name ${_AGENT_NAME} \
              --location ${_REGION} \
              --requirements-file requirements.txt \
              --extra-packages ./app
    
    substitutions:
      _REGION: us-central1
      _AGENT_NAME: my-first-agent
    
    options:
      substitutionOption: ALLOW_LOOSE
      defaultLogsBucketBehavior: REGIONAL_USER_OWNED_BUCKET
    
    ```

2.  変更を保存し、再度 `gcloud builds submit` を実行すると、デプロイ後に評価が自動的に実行されるようになります。
    **この処理も数分かかります。** 待ち時間に、先ほど編集した `agents/cloudbuild.yaml` を見返し、`eval` ステップがどのように追加されたかを確認してみましょう。
    ```bash
    gcloud builds submit . --config cloudbuild.yaml \
         --substitutions=_REGION=us-central1,_AGENT_NAME=my-awesome-agent
    ```
    これにより、デプロイのたびに品質が保証されるようになります。
    このデプロイとは独立して次のセクションを実施できるため、Cloud Shell をもう一つ開き、先に進めることもできます。


## 8. ローカルの Python Web App から Agent Engine を叩く


`client` ディレクトリにあるStreamlit製のWebアプリケーションから、デプロイ済みのAgent Engineを呼び出します。

1.  **クライアント環境のセットアップ**:
    `agents` ディレクトリから `client` ディレクトリに移動し、Webアプリケーション用の仮想環境をセットアップします。
    ```bash
    cd ../client
    uv venv venv
    source venv/bin/activate
    uv pip install -r requirements.txt
    ```

2.  **エージェントの指定**:
    `client/webapp.py` を開き、`agent_engines.get()` の引数を、ご自身がデプロイしたエージェントのリソース名に書き換えます。リソース名は、デプロイ時のログやGoogle Cloudコンソールの `Vertex AI > Agent Engine` のページから確認できます。

    ```python
    # client/webapp.py

    # ... (省略) ...
    # Agentの初期化
    # 例: "projects/your-project-id/locations/us-central1/reasoningEngines/1234567890"
    agent = agent_engines.get("[YOUR_AGENT_ENGINE_RESOURCE_NAME]") 
    # ... (省略) ...
    ```

3.  **アプリケーションの起動**:
    以下のコマンドでWebアプリを起動します。
    ```bash
    streamlit run webapp.py --server.enableCORS=false
    ```
    コマンド実行後、Webアプリの画面がブラウザに表示されるまで少し時間がかかる場合があります。

4.  ブラウザで表示されたWebアプリから、ユーザーIDとメッセージを入力してエージェントと対話できることを確認します。
    これで、WebアプリケーションとAIエージェントの連携が確認できました。

## 9. Python Web App を Cloud Run にデプロイする

次に、このWebアプリケーションをCloud Runにデプロイします。

1.  `client` ディレクトリにいることを確認してください。

2.  以下のコマンドを実行して、Cloud Build経由でCloud Runにデプロイします。Cloud Build は、実行されているプロジェクトのIDを自動的に `PROJECT_ID` として利用します。
    ```bash
    gcloud builds submit . --config cloudbuild.yaml \
        --substitutions=_SERVICE_NAME=client-agent,_REGION=us-central1,_TAG=latest
    ```
    このコマンドは、`Dockerfile` を使ってコンテナイメージをビルドし、Cloud Runにデプロイします。
    **デプロイには数分かかります。** 待ち時間に、Webアプリケーション本体のコード (`client/webapp.py`) や、コンテナの定義ファイル (`client/Dockerfile`) を読んで、どのような処理が行われているか確認してみましょう。


3.  デプロイが完了すると、出力に表示されるURLからWebアプリケーションにアクセスできます。
    世界中のどこからでもアクセス可能なWebアプリケーションが完成しました。

## 10. Cloud Run に IAP を設定する

最後に、デプロイしたWebアプリケーションにIAPを設定して、認証されたユーザーのみがアクセスできるようにします。

1.  **IAPを有効にする**: 以下のコマンドで、Cloud Runサービスを更新してIAPを有効にします。`_SERVICE_NAME` はCloud Runのサービス名（例: `client-agent`）です。
    ```bash
    gcloud beta run services update client-agent \
      --region="us-central1" \
      --iap
    ```

2. **認証がかかっていることを確認する**: さきほどデプロイした Cloud run の url にアクセスします。

3.  **アクセス権限の付与**: IAP経由でのアクセスを許可したいユーザー（またはグループ、サービスアカウント）に `IAP-secured Web App User` ロールを付与します。
    ```bash
    gcloud beta iap web add-iam-policy-binding \
      --member=user:[USER_EMAIL] \
      --role=roles/iap.httpsResourceAccessor \
      --region=us-central1 \
      --resource-type=cloud-run \
      --service=client-agent
    ```
    `[USER_EMAIL]` にはアクセスを許可したいユーザーのメールアドレスを指定します。

これで、指定したユーザーのみがWebアプリケーションにアクセスできるようになりました。

## 11. おわりに

このチュートリアルでは、Generative AI Agentの開発からデプロイ、評価、Webアプリへの統合、そしてセキュリティ設定まで、一連のライフサイクルを体験しました。ここからさらに、エージェントの能力を拡張したり、より複雑なワークフローを構築したりすることに挑戦してみてください。

### 11.1 おまけ：Stateful Agentを試す

このハンズオンには、会話の状態を記憶できる `agent_stateful.py` が含まれています。
`adk web` を使って、このエージェントの動作をローカルで確認してみましょう。
1.  agents フォルダに移動します
    ```bash
    cd ../agents
    source venv/bin/activate
    ```
2.  `app/__init__.py` ファイルを開きます。

3.  インポートするエージェントを `agent.py` から `agent_stateful.py` に変更します。

    ```python
    # agents/app/__init__.py

    # from .agent import root_agent  # この行をコメントアウト
    from .agent_stateful import root_agent
    ```

4.  `agents` ディレクトリで `adk web` を実行します。
    ```bash
    adk web .
    ```

5.  Web UIで、以下のよう順番に対話を試してみてください。
    - **"今日の東京の天気は？"** 
    - **"これからは気温を華氏で教えてください"**
    - **"改めて東京は？"**

このように、`agent_stateful.py` は `ToolContext` を使ってセッション内に状態（この場合は温度の単位）を保存し、次の応答に活かすことができます。
確認が終わったら、`__init__.py` の変更を元に戻しておきましょう。
