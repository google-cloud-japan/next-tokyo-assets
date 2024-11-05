# **丸わかり！生成 AI アプリケーション開発パターン**

## **ハンズオン概要**

本ハンズオンでは Google Cloud のマネージドサービスをフル活用し、生成 AI を組み込んだ実際に動作する複数のアプリケーションを構築、デプロイします。このハンズオンだけで生成 AI アプリのトレンドを掴んで頂けるように、最新のユースケースを幅広くカバーします。生成 AI を実際のアプリケーションに組み込む場合のプラクティスについて興味がある方、Google Cloud + 生成 AI でどのようなことができるのかを網羅的に体験したい方におすすめです。

以下が今回のハンズオンで利用する主要なサービスです。

**Cloud Run**

- Dockerfile、ソースコードから 1 コマンドで Cloud Run にデプロイ
- プライベートリリース (タグをつけたリリース) などのトラフィック コントロール
- 複数のサービスを Cloud Run で動かし連携させる

**Firebase**

- 認証 (Firebase Authentication)
- NoSQL データベース (Firestore)
- オブジェクトストレージ (Cloud Storage for Firebase)

**Vertex AI**

- 生成 AI の API (Gemini 1.5 Flash)
- RAG 機能を司る API 群 (RAG Engine)

今回は以下の 2 つのアプリケーションを構築していくことで、Google Cloud を使った生成 AI のアプリケーション組み込みを学びます。

- UI、または UI に関わるフロントエンド機能を提供するアプリケーション (AI organizer)
- 生成 AI 機能を担当するバックエンドアプリケーション (GenAI backend)

## **Google Cloud プロジェクトの確認**

開いている Cloud Shell のプロンプトに `(黄色の文字)` の形式でプロジェクト ID が表示されていることを確認してください。

これが表示されている場合は、Google Cloud のプロジェクトが正しく認識されています。

表示されていない場合は、以下の手順で Cloud Shell を開き直して下さい

1. Cloud Shell を閉じる
1. 上のメニューバーのプロジェクト選択部分で払い出されたプロジェクトが選択されていることを確認する。
1. Cloud Shell を再度開く

## **参考: Cloud Shell の接続が途切れてしまったときは?**

一定時間非アクティブ状態になる、またはブラウザが固まってしまったなどで `Cloud Shell` の接続が切れてしまう場合があります。

その場合は `再接続` をクリックした後、以下の対応を行い、チュートリアルを再開してください。

![再接続画面](https://raw.githubusercontent.com/GoogleCloudPlatform/gcp-getting-started-lab-jp/master/workstations_with_generative_ai/images/reconnect_cloudshell.png)

### **1. チュートリアル資材があるディレクトリに移動する**

```bash
cd ~/next-tokyo-assets/2024/genai-app-patterns
```

### **2. チュートリアルを開く**

```bash
teachme tutorial_ja.md
```

途中まで進めていたチュートリアルのページまで `Next` ボタンを押し、進めてください。

## **Google Cloud 環境設定**

### **1. Google Cloud 機能有効化**

Google Cloud では利用したい機能（API）ごとに、有効化を行う必要があります。

ここで、以降のハンズオンで利用する機能を事前に有効化しておきます。

```bash
gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  firestore.googleapis.com \
  pubsub.googleapis.com \
  eventarc.googleapis.com \
  aiplatform.googleapis.com \
  translate.googleapis.com \
  firebasestorage.googleapis.com
```

`Cloud Shell の承認` が表示された場合は、`承認` をクリックします。

**GUI**: [API ライブラリ](https://console.cloud.google.com/apis/library)

### **2. Terraform の初期化**

本ハンズオンではいくつかの設定を作成済みの Terraform スクリプトを利用します。

そのために **Terraform の実行環境を初期化**します。

```bash
(cd tf/ && terraform init)
```

### **3. Vertex AI 関連機能の有効化**

[Vertex AI](https://console.cloud.google.com/vertex-ai) にアクセスし `すべての推奨 API を有効化` ボタンをクリックします。

<walkthrough-footnote>必要な機能が使えるようになりました。次に Firebase の設定方法を学びます。</walkthrough-footnote>

## **Firebase プロジェクトの設定**

AI organizer では Firebase の機能をフル活用し、リアルタイム性の高い UI を構築しています。

**GUI** から Firebase を有効化します。

1. [Firebase コンソール](https://console.firebase.google.com/) にブラウザからアクセスします。
1. `プロジェクトを作成` ボタンをクリックします。
1. 最下部の `Cloud プロジェクトに Firebase を追加` をクリックします。
1. `Google Cloud プロジェクトを選択する` から qwiklabs で利用しているプロジェクトを選択します。
1. 規約への同意、利用目的のチェックマークを入れ、`続行` をクリックします。

   料金確認画面が表示された場合は、`プランを確認` ボタンをクリックします。

1. Google Cloud プロジェクトに Firebase を追加する際に注意すべき点

   `続行` をクリックします。

1. Google アナリティクス（Firebase プロジェクト向け）

   `このプロジェクトで Google アナリティクスを有効にする` をオフにし、`Firebase を追加` をクリックします。

1. `Firebase プロジェクトが準備できました` と表示されたら `続行` をクリックします。

## **Firebase アプリケーションの設定**

### **1. Firebase アプリケーションの作成**

```bash
firebase apps:create -P $GOOGLE_CLOUD_PROJECT WEB ai-organizer
```

### **2. Firebase 設定のアプリケーションへの埋め込み**

```bash
./scripts/firebase_config.sh ./src/ai-organizer
```

全ての NEXT_PUBLIC_FIREBASE_XXXX という出力の右辺 (=より後ろ) に、文字列が設定されていれば成功です。

## **Firebase Authentication の設定**

認証に関わる機能全般を Firebase Authentication を用いて実装します。

この機能を利用することで、メールアドレスとパスワードを利用した基本的な認証機能から、Google、Facebook といったソーシャルログインを簡単に実現することができます。

今回は、簡単に使うために**メールアドレスとパスワードの認証**を利用します。

```bash
(cd tf/ && terraform apply -target=google_identity_platform_config.default -var="project_id=$GOOGLE_CLOUD_PROJECT" -auto-approve)
```

**GUI**: 以下のコマンドを実行し出力された URL にアクセスすると Firebase コンソールからの設定画面が確認可能です。

```bash
echo https://console.firebase.google.com/project/${GOOGLE_CLOUD_PROJECT}/authentication/providers?hl=ja
```

## **Firestore データベース、セキュリティルールの設定**

AI organizer で利用する各種メタデータの保存先として　 Firestore を利用します。

Firestore は NoSQL データベースの一つで、データをドキュメントの形で保存します。

また Firestore は**クライアント (今回の場合は利用者それぞれのブラウザ) から直接データベースを操作できる**という大きな特徴があり、今回もその機能を活用し、リアルタイム性の高い UI を実現しています。

- ユーザーの環境が準備できたら UI に反映
- ファイルがアップロードされたら UI に反映

```bash
(cd tf/ && terraform apply -target=google_firestore_database.default -target=google_firebaserules_ruleset.firestore -target=google_firebaserules_release.firestore -var="project_id=$GOOGLE_CLOUD_PROJECT" -auto-approve)
```

### **セキュリティについて**

クライアントから直接操作ができるということは、正しいセキュリティの設定をしておかないと、誰でもデータの閲覧、上書きができてしまうということになります。

Cloud Firestore では**セキュリティルール**という機能を使い、以下のようにセキュリティを高めることができます。

- Firebase Authentication でログイン済みのユーザーのみデータを閲覧
- 自分のデータのみ書き込み可能

今回は Terraform スクリプトの中で最低限のセキュリティルールを適用しています。

**GUI**: 以下のコマンドを実行し出力された URL にアクセスすると Firebase コンソールからルール画面が確認可能です。

```bash
echo https://console.firebase.google.com/project/${GOOGLE_CLOUD_PROJECT}/firestore/databases/-default-/rules?hl=ja
```

## **Cloud Storage for Firebase、セキュリティルールの設定**

AI organizer では生成 AI に回答させる際のソースデータとしてファイルをアップロードができます。

アップロードしたファイルは Cloud Storage for Firebase に保存されます。

Firestore と同様に Cloud Storage for Firebase では**クライアントから直接ファイルを Cloud Storage にアップロード**できます。

```bash
(cd tf/ && terraform apply -target=null_resource.create_firebase_storage_default_bucket -target=google_firebaserules_ruleset.storage -target=google_firebaserules_release.storage -var="project_id=$GOOGLE_CLOUD_PROJECT" -auto-approve)
```

### **セキュリティについて**

セキュリティについても Firestore と同様、クライアントから直接操作する関係上、設定が必須となります。

Cloud Storage for Firebase でも**セキュリティルール**を利用してセキュリティを確保します。また Terraform で設定済みです。

今回は Firebase Authentication でログインしたユーザーが、**Cloud Storage 上の自分専用のフォルダ配下にのみ書き込み、読み込みができる**ようにしています。

**GUI**: 以下のコマンドを実行し出力された URL にアクセスすると Firebase コンソールからルール画面が確認可能です。

```bash
echo https://console.firebase.google.com/project/${GOOGLE_CLOUD_PROJECT}/storage/${GOOGLE_CLOUD_PROJECT}.firebasestorage.app/rules?hl=ja
```

## **AI organizer を Cloud Run にデプロイ**

Cloud Run では様々な方法でデプロイが可能です。ここでは以下の方法でアプリケーションをデプロイします。

- Dockerfile を利用して、ソースファイルから 1 コマンドで Cloud Run にデプロイ

### **1. サービスアカウントの作成**

デフォルトでは Cloud Run にデプロイされたアプリケーションは強い権限を持ちます。最小権限の原則に従い、必要最小限の権限を持たせるため、まずサービス用のアカウントを作成します。

```bash
gcloud iam service-accounts create ai-organizer-sa
```

### **2. サービスアカウントへの権限追加**

AI organizer は認証情報の操作、Firestore の読み書き権限が必要です。先程作成したサービスアカウントに権限を付与します。

```bash
gcloud projects add-iam-policy-binding $GOOGLE_CLOUD_PROJECT \
  --member serviceAccount:ai-organizer-sa@$GOOGLE_CLOUD_PROJECT.iam.gserviceaccount.com \
  --role 'roles/firebaseauth.admin'
gcloud projects add-iam-policy-binding $GOOGLE_CLOUD_PROJECT \
  --member serviceAccount:ai-organizer-sa@$GOOGLE_CLOUD_PROJECT.iam.gserviceaccount.com \
  --role 'roles/iam.serviceAccountTokenCreator'
```

### **3. AI organizer のデプロイ**

Cloud Run にソースコードを 1 コマンドでデプロイします。

```bash
gcloud run deploy ai-organizer \
  --source ./src/ai-organizer \
  --service-account ai-organizer-sa@$GOOGLE_CLOUD_PROJECT.iam.gserviceaccount.com \
  --allow-unauthenticated \
  --region asia-northeast1 \
  --quiet
```

**注**: デプロイ完了まで最大 10 分程度かかります。

### **4. (Optional) コンテナのビルドログを確認する**

上記 3 の手順は時間がかかるため、コンテナのビルドログを確認します。

コマンド実行中の出力に `Building Container... Logs are available at [https://console.cloud.google.com/〜]` と記載があります。

ここで `https://console.〜` の URL をコピーし (URL をカーソルでなぞると自動的にコピーされます) ブラウザの新しいタブにペーストし開くと、リアルタイムのコンテナビルドログを確認できます。

## **生成 AI 関連機能 (GenAI backend) の追加**

生成 AI 関連の以下の処理を実行する GenAI backend をデプロイします。

- ユーザーの追加をトリガーに、ユーザー個別の検索インデックス (Corpus) を作成
- ファイルアップロードをトリガーに、ファイルをソースとしてインデックスに追加
- ソースの削除をトリガーに、インデックスからソースを削除
- ユーザーからの質問をトリガーに、インデックスを利用して回答を生成

今回は、GenAI backend も個別の Cloud Run サービスでデプロイし、UI を担当する AI organizer と連携させるようにします。

## **GenAI backend のデプロイ**

### **1. サービスアカウントの作成**

GenAI backend 用のアカウントを作成します。

```bash
gcloud iam service-accounts create genai-backend-sa
```

### **2. サービスアカウントへの権限追加**

生成 AI 処理アプリケーションは Cloud Storage、Vertex AI, Firestore などのサービスへのアクセス権限が必要です。

```bash
gcloud projects add-iam-policy-binding $GOOGLE_CLOUD_PROJECT \
  --member serviceAccount:genai-backend-sa@$GOOGLE_CLOUD_PROJECT.iam.gserviceaccount.com \
  --role roles/aiplatform.user
gcloud projects add-iam-policy-binding $GOOGLE_CLOUD_PROJECT \
  --member serviceAccount:genai-backend-sa@$GOOGLE_CLOUD_PROJECT.iam.gserviceaccount.com \
  --role roles/storage.objectUser
gcloud projects add-iam-policy-binding $GOOGLE_CLOUD_PROJECT \
  --member=serviceAccount:genai-backend-sa@$GOOGLE_CLOUD_PROJECT.iam.gserviceaccount.com \
  --role=roles/eventarc.eventReceiver
gcloud projects add-iam-policy-binding $GOOGLE_CLOUD_PROJECT \
  --member serviceAccount:genai-backend-sa@$GOOGLE_CLOUD_PROJECT.iam.gserviceaccount.com \
  --role roles/datastore.user
```

### **3 GenAI backend のデプロイ**

```bash
gcloud run deploy genai-backend \
  --source ./src/genai-backend \
  --region asia-northeast1 \
  --service-account genai-backend-sa@$GOOGLE_CLOUD_PROJECT.iam.gserviceaccount.com \
  --set-env-vars=FLASK_PROJECT_ID=$GOOGLE_CLOUD_PROJECT \
  --no-allow-unauthenticated
```

## **非同期処理 (Eventarc) の設定**

AI organizer には生成 AI 関連の機能が入っていないため、アプリケーション全体として機能しない状態です。

**生成 AI 関連の処理は少し時間がかかるものが多い**ため、本ハンズオンでは生成 AI の処理を GenAI backend に切り出し、非同期で処理するようにします。

また今回のアーキテクチャのポイントですが、**非同期の連携はサービス同士が直接連携する形ではなく、データストアへの操作をトリガーに連携**します。

具体的には以下のような処理をトリガーに、次の処理が行われます。

- ユーザー情報の作成 -> ユーザー個別の検索インデックス (Corpus) を作成
- ファイルをアップロード、ファイルメタデータを作成 -> ファイルをソースとしてインデックスに追加
- ファイルメタデータを削除待ち状態に変更 -> インデックスからソースを削除、元ファイルを Cloud Storage から削除
- ユーザーからの質問を作成 -> 保存されている質問履歴を元に回答を生成

### **1. 前準備**

```bash
SERVICE_ACCOUNT="$(gsutil kms serviceaccount -p $GOOGLE_CLOUD_PROJECT)"
gcloud projects add-iam-policy-binding $GOOGLE_CLOUD_PROJECT \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role='roles/pubsub.publisher'
gcloud run services add-iam-policy-binding genai-backend \
  --member="serviceAccount:genai-backend-sa@${GOOGLE_CLOUD_PROJECT}.iam.gserviceaccount.com" \
  --role='roles/run.invoker' \
  --region asia-northeast1
```

### **2. Eventarc トリガーの作成**

ここでは本ステップ上部に記載している 4 つのトリガーをまとめて作成します。

各コマンドのポイントは、**Firestore のどのようなデータ**に対して、**どのような更新**が行われたときに、**どの処理 (Cloud Run) を呼ぶのか**がオプションで設定されています。

```bash
gcloud eventarc triggers create genai-backend-add-user \
  --location=asia-northeast1 \
  --destination-run-service=genai-backend \
  --destination-run-region=asia-northeast1 \
  --event-filters="type=google.cloud.firestore.document.v1.created" \
  --event-filters="database=(default)" \
  --event-filters-path-pattern="document=users/{uid}" \
  --service-account=genai-backend-sa@$GOOGLE_CLOUD_PROJECT.iam.gserviceaccount.com \
  --event-data-content-type="application/protobuf" \
  --destination-run-path="/add_user" && \
gcloud eventarc triggers create genai-backend-add-source \
  --location=asia-northeast1 \
  --destination-run-service=genai-backend  \
  --destination-run-region=asia-northeast1 \
  --event-filters="type=google.cloud.firestore.document.v1.created" \
  --event-filters="database=(default)" \
  --event-filters-path-pattern="document=users/{uid}/notebooks/{notebookId}/sources/{sourceId}" \
  --service-account=genai-backend-sa@$GOOGLE_CLOUD_PROJECT.iam.gserviceaccount.com \
  --event-data-content-type="application/protobuf" \
  --destination-run-path="/add_source" && \
gcloud eventarc triggers create genai-backend-update-source \
  --location=asia-northeast1 \
  --destination-run-service=genai-backend \
  --destination-run-region=asia-northeast1 \
  --event-filters="type=google.cloud.firestore.document.v1.updated" \
  --event-filters="database=(default)" \
  --event-filters-path-pattern="document=users/{uid}/notebooks/{notebookId}/sources/{sourceId}" \
  --service-account=genai-backend-sa@$GOOGLE_CLOUD_PROJECT.iam.gserviceaccount.com \
  --event-data-content-type="application/protobuf" \
  --destination-run-path="/update_source" && \
gcloud eventarc triggers create genai-backend-question \
  --location=asia-northeast1 \
  --destination-run-service=genai-backend  \
  --destination-run-region=asia-northeast1 \
  --event-filters="type=google.cloud.firestore.document.v1.created" \
  --event-filters="database=(default)" \
  --event-filters-path-pattern="document=users/{uid}/notebooks/{notebookId}/chat/{messageId}" \
  --service-account=genai-backend-sa@$GOOGLE_CLOUD_PROJECT.iam.gserviceaccount.com \
  --event-data-content-type="application/protobuf" \
  --destination-run-path="/question"
```

以下のようなエラーが出た場合は、少し待ってから再度コマンドを実行してください。

```
ERROR: (gcloud.eventarc.triggers.create) FAILED_PRECONDITION: Invalid resource state for "": Permission denied while using the Eventarc Service Agent.
```

## **非同期連携の設定**

今の非同期連携では以下の 2 つの問題があります。

- 各非同期処理が 10 秒以内に終わらないと、エラー扱いになりリトライしてしまう
- リトライ回数に制限がなく、アプリケーションのバグなどで処理が失敗するとリトライされ続けてしまう＝リソースコストが上がり続けてしまう

これを解決するために以下の設定を行います。

- 各非同期処理の処理待ち時間を 300 秒 (5 分) に修正
- 最小リトライの間隔を 300 秒 (5 分) に修正
- 合計 5 回非同期の処理に失敗したら、リトライをやめる (デッドレタートピックに入れる)

### **1. デッドレタートピックの作成**

```bash
gcloud pubsub topics create genai-backend-dead-letter
```

### **2. デッドレタートピック関連の権限設定**

```bash
PROJECT_NUMBER=$(gcloud projects describe $GOOGLE_CLOUD_PROJECT --format="value(projectNumber)")
gcloud pubsub topics add-iam-policy-binding genai-backend-dead-letter \
  --member="serviceAccount:service-$PROJECT_NUMBER@gcp-sa-pubsub.iam.gserviceaccount.com" \
  --role="roles/pubsub.publisher"
```

### **3. デッドレタートピックの設定、サブスクリプションの処理待ち時間、最小リトライ間隔の修正**

```bash
./scripts/setup_eventarc_subscription.sh genai-backend-add-user && \
./scripts/setup_eventarc_subscription.sh genai-backend-add-source && \
./scripts/setup_eventarc_subscription.sh genai-backend-update-source && \
./scripts/setup_eventarc_subscription.sh genai-backend-question
```

## **ソースデータに基づいた回答生成**

ソースデータに基づいた回答生成は RAG というテクニックを [RAG Engine](https://cloud.google.com/vertex-ai/generative-ai/docs/rag-overview) を利用して実現しています。

ここでは具体的なソースコードを見ながら、詳細な処理を確認します。

RAG は一般的に大きくデータを準備する前処理と、質問への回答を生成する処理の 2 つに分かれています。

データを準備する前処理は以下の手順で行われます。

1. データの取り込み
1. データの変換
1. エンべディング化
1. データのインデックス化

上記の一連の手続きがソースコードでは<walkthrough-editor-select-line filePath="./next-tokyo-assets/2024/genai-app-patterns/src/genai-backend/main.py" startLine="65" endLine="74" startCharacterOffset="0" endCharacterOffset="5">こちら</walkthrough-editor-select-line>に該当します。

質問への回答生成は以下の手順で行われ、ソースコードの該当箇所を示します。

1. <walkthrough-editor-select-line filePath="./next-tokyo-assets/2024/genai-app-patterns/src/genai-backend/main.py" startLine="176" endLine="189" startCharacterOffset="4" endCharacterOffset="5">質問に関連するデータをインデックスから取得</walkthrough-editor-select-line>
1. <walkthrough-editor-select-line filePath="./next-tokyo-assets/2024/genai-app-patterns/src/genai-backend/main.py" startLine="191" endLine="195" startCharacterOffset="4" endCharacterOffset="5">インデックスから取得したデータを生成 AI にセット</walkthrough-editor-select-line>

## **マルチターンの質問回答**

過去の質問内容、回答内容を踏まえた質問回答 (マルチターンの質問回答) を生成するには、**生成 AI に対して現在の質問に加えて、今までのやり取りも合わせて送る**必要があります。

つまり生成 AI は今までのやり取りを記憶しているわけではなく、プログラム側で対応が必要になります。

今回のプログラムでは Firestore に質問と回答の履歴を持つようにし、質問を投げたときに履歴すべてを質問に合わせて送るようにしています。

具体的な処理部分を以下に示します。

- <walkthrough-editor-select-line filePath="./next-tokyo-assets/2024/genai-app-patterns/src/genai-backend/main.py" startLine="197" endLine="203" startCharacterOffset="4" endCharacterOffset="5">過去の履歴を取得</walkthrough-editor-select-line>
- <walkthrough-editor-select-line filePath="./next-tokyo-assets/2024/genai-app-patterns/src/genai-backend/main.py" startLine="211" endLine="211" startCharacterOffset="8" endCharacterOffset="65">過去の履歴を含め質問を送信</walkthrough-editor-select-line>

## **AI organizer の試用 (ユーザー登録からソースのアップロード)**

### **1. アプリケーションへブラウザからアクセス**

エディタが開いている場合は、`ターミナルを開く` をクリックしターミナルを開きます。

以下コマンドを実行して出力された URL をクリックすると、ブラウザのタブが開きログイン画面が起動します。

```bash
gcloud run services describe ai-organizer --region asia-northeast1 --format json | jq -r '.status.address.url'
```

### **2. 新規ユーザーの登録**

最下部の `アカウントを作成する場合はこちら` をクリックし、ユーザー情報を入力、`アカウントを登録する` をクリックします。

メールアドレス、パスワードは存在しないものでも問題ありません。

うまく登録ができると、ノートブック管理画面に遷移します。ユーザーの初期化のため少し待ち時間があります。

### **3. 新規ノートブックの作成**

- `新しいノートブック` カードをクリックします。そうすると新しくノートブックが作成され、詳細ページに遷移します。

### **4. ソースの追加**

1. 左メニューの中の `ソース` の右にある ＋ のようなアイコンをクリックします。
1. 手持ちの PDF、または以下のサンプル PDF をダウンロードし、アップロードします。
1. 少し待つと読み込み処理が完了し、ロード中のスピナーが消えます。

**サンプル PDF 一覧**

[Google Cloud ホワイトペーパー](https://cloud.google.com/whitepapers?hl=ja) で公開されている PDF ファイルをダウンロードしてください。

- [クラウドチームの編成](https://services.google.com/fh/files/misc/designing_cloud_teams.pdf)
- [Google Cloud の AI 導入フレームワーク](https://services.google.com/fh/files/misc/ai_adoption_framework_whitepaper.pdf)
- [Google Cloud 導入フレームワーク](https://services.google.com/fh/files/misc/google_cloud_adoption_framework_whitepaper.pdf)
- [統合データ分析プラットフォームの構築](https://services.google.com/fh/files/misc/googlecloud_unified_analytics_data_platform_paper_2021.pdf)
- [データベースを強みにする](https://services.google.com/fh/files/misc/guide_to_google_cloud_databases.pdf)
- [クラウドのデータ ガバナンスに関する原則とベスト プラクティス](https://services.google.com/fh/files/misc/principles_best_practices_for_data-governance.pdf)
- [マイクロサービスでクラウド ネイティブなアプローチを採用](https://cloud.google.com/files/Cloud-native-approach-with-microservices.pdf)

## **AI organizer の試用 (アップロードしたファイルについての質問)**

### **1. ソースに関連する質問**

アップロードしたソースのチェックボックスをチェックし、最下部の質問バーから質問を入力します。
サンプル PDF ごとの質問文例を記載します。

- [クラウドチームの編成](https://services.google.com/fh/files/misc/designing_cloud_teams.pdf)

  ```text
  クラウドチーム編成のベストプラクティスを教えて下さい
  ```

- [Google Cloud の AI 導入フレームワーク](https://services.google.com/fh/files/misc/ai_adoption_framework_whitepaper.pdf)

  ```text
  AI を導入する手順を簡潔に教えて下さい
  ```

- [Google Cloud 導入フレームワーク](https://services.google.com/fh/files/misc/google_cloud_adoption_framework_whitepaper.pdf)

  ```text
  Google Cloud を使い始めるにはまず何からやるべきですか
  ```

- [統合データ分析プラットフォームの構築](https://services.google.com/fh/files/misc/googlecloud_unified_analytics_data_platform_paper_2021.pdf)

  ```text
  データ分析プラットフォームを統合するデメリットはありますか
  ```

- [データベースを強みにする](https://services.google.com/fh/files/misc/guide_to_google_cloud_databases.pdf)

  ```text
  Google Cloud のデータベースの強みを教えて下さい
  ```

- [クラウドのデータ ガバナンスに関する原則とベスト プラクティス](https://services.google.com/fh/files/misc/principles_best_practices_for_data-governance.pdf)

  ```text
  クラウドのデータガバナンスの原則を簡潔に教えて下さい
  ```

- [マイクロサービスでクラウド ネイティブなアプローチを採用](https://cloud.google.com/files/Cloud-native-approach-with-microservices.pdf)

  ```text
  マイクロサービスのメリットは何ですか
  ```

うまくいくと、アップロードしたファイルの内容をベースに回答が生成されます。

### **2. 気に入った回答を保存する**

気に入った回答の右上にあるピンボタンをクリックすると、メモとして保存することが可能です。

### **3. 色々活用してみる**

手持ちの PDF などをアップロードし、回答に利用したい PDF を選択、質問を繰り返してどのような回答になるかを体験してみてください。

### **4. ログアウトする**

画面の右上のアイコン (扉からでていくマーク) をクリックするとログアウトが可能です。

### **5. 新規ユーザーを作成し、データが別管理になっていることを確認する**

新しいユーザーを作成し、動作を確認してみてください。

ユーザーごとにデータが分けられて管理されており、先程アップロードしたデータは見えないことがわかります。

## **要約生成機能の追加**

新機能として、生成 AI を利用したドキュメントの要約生成機能を追加します。

ここでも非同期での連携方式を採用します。

すでに GenAI backend には該当のソースコードは含まれているため、Eventarc を利用した連携を設定します。

### **1. Eventarc トリガーの作成**

```bash
gcloud eventarc triggers create genai-backend-summarize \
  --location=asia-northeast1 \
  --destination-run-service=genai-backend  \
  --destination-run-region=asia-northeast1 \
  --event-filters="type=google.cloud.firestore.document.v1.created" \
  --event-filters="database=(default)" \
  --event-filters-path-pattern="document=users/{uid}/notebooks/{notebookId}/sources/{sourceId}" \
  --service-account=genai-backend-sa@$GOOGLE_CLOUD_PROJECT.iam.gserviceaccount.com \
  --event-data-content-type="application/protobuf" \
  --destination-run-path="/summarize"
```

ソースデータが Firestore に新規作成されたときに、GenAI backend サービス (Cloud Run) のパス (/summarize) を呼び出します。

### **2. デッドレタートピックの設定、サブスクリプションの処理待ち時間、最小リトライ間隔の修正**

```bash
./scripts/setup_eventarc_subscription.sh genai-backend-summarize
```

### **3. ソースコードのポイント**

ファイルの要約は様々な作成の方法があります。

例えば、長いファイルは細かく分割しながら処理をしていくなどの方法があります。

今回は Gemini 1.5 Flash の特徴である、**ロングコンテキスト (100 万トークン) の入力を活かし特別な処理無しに一回でファイルを読み込み**、要約を生成しています。

- <walkthrough-editor-select-line filePath="./next-tokyo-assets/2024/genai-app-patterns/src/genai-backend/main.py" startLine="296" endLine="301" startCharacterOffset="4" endCharacterOffset="6">要約生成のプロンプト</walkthrough-editor-select-line>
- <walkthrough-editor-select-line filePath="./next-tokyo-assets/2024/genai-app-patterns/src/genai-backend/main.py" startLine="305" endLine="305" startCharacterOffset="8" endCharacterOffset="87">要約を生成</walkthrough-editor-select-line>

### **4. 要約生成機能の試用**

なにかソースファイルをアップロードしてみてください。

ソースファイルに対する要約が生成されると、**ファイル名が太字で表示**され、**ファイル名をクリック**すると要約が確認可能です。

## **一般的な質問生成機能の追加**

中身をあまり理解していないドキュメントをアップロードした場合、質問を考えるのも難しい場合があります。

そこで新機能としてドキュメントに関する一般的な質問を生成する機能を追加します。

ここでも非同期での連携方式を採用し、すでに GenAI backend には該当のソースコードは含まれているため、Eventarc を利用した連携を設定します。

### **1. Eventarc トリガーの作成**

```bash
gcloud eventarc triggers create genai-backend-generate-common-questions \
  --location=asia-northeast1 \
  --destination-run-service=genai-backend  \
  --destination-run-region=asia-northeast1 \
  --event-filters="type=google.cloud.firestore.document.v1.created" \
  --event-filters="database=(default)" \
  --event-filters-path-pattern="document=users/{uid}/notebooks/{notebookId}/sources/{sourceId}" \
  --service-account=genai-backend-sa@$GOOGLE_CLOUD_PROJECT.iam.gserviceaccount.com \
  --event-data-content-type="application/protobuf" \
  --destination-run-path="/generate_common_questions"
```

ソースデータが Firestore に新規作成されたときに、GenAI backend サービス (Cloud Run) のパス (/generate_common_questions) を呼び出します。

### **2. デッドレタートピックの設定、サブスクリプションの処理待ち時間、最小リトライ間隔の修正**

```bash
./scripts/setup_eventarc_subscription.sh genai-backend-generate-common-questions
```

### **3. ソースコードのポイント**

ここでも Gemini 1.5 Flash の特徴である **ロングコンテキスト** を活かして、プロンプトだけで質問例を生成しています。

- <walkthrough-editor-select-line filePath="./next-tokyo-assets/2024/genai-app-patterns/src/genai-backend/main.py" startLine="341" endLine="345" startCharacterOffset="4" endCharacterOffset="73">質問生成のプロンプト</walkthrough-editor-select-line>
- <walkthrough-editor-select-line filePath="./next-tokyo-assets/2024/genai-app-patterns/src/genai-backend/main.py" startLine="351" endLine="351" startCharacterOffset="8" endCharacterOffset="87">質問を生成</walkthrough-editor-select-line>

### **4. 質問生成機能の試用**

なにかソースファイルをアップロードしてみてください。

ソースファイルに対する質問が生成されると、ソースファイルを選択 (チェックボックスを選択) すると、質問文を入力するフォームの上に質問文例が表示されます。

質問例をクリックをすると、その質問を投げることができます。

## **Congratulations!**

<walkthrough-conclusion-trophy></walkthrough-conclusion-trophy>

これにて**丸わかり！生成 AI アプリケーション開発パターン**は完了です。

Qwiklabs に戻り、`ラボを終了` ボタンをクリックし、ハンズオンを終了します。
