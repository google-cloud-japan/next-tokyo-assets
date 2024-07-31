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
- RAG 機能を司る API 群 (LlamaIndex on Vertex AI for RAG)

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

<walkthrough-footnote>必要な機能が使えるようになりました。次に Firebase の設定方法を学びます。</walkthrough-footnote>

## **Firebase プロジェクトの設定**

AI organizer では Firebase の機能をフル活用し、リアルタイム性の高い UI を構築しています。

### **1. Firebase プロジェクトの有効化**

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

**Firebase console での作業はここまでになります。このあとは Cloud Shell に戻り操作を行ってください**

### **2. Terraform の初期化**

本ハンズオンではいくつかの設定を作成済みの Terraform スクリプトを利用します。

そのために **Terraform の実行環境を初期化**します。

```bash
(cd tf/ && terraform init)
```

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

## **Cloud Storage for Firebase、セキュリティルールの設定**

AI organizer では生成 AI に回答させる際のソースデータとしてファイルをアップロードができます。

アップロードしたファイルは Cloud Storage for Firebase に保存されます。

Firestore と同様に Cloud Storage for Firebase では**クライアントから直接ファイルを Cloud Storage にアップロード**できます。

```bash
(cd tf/ && terraform apply -target=google_app_engine_application.default -target=google_firebase_storage_bucket.default -target=google_firebaserules_ruleset.storage -target=google_firebaserules_release.storage -var="project_id=$GOOGLE_CLOUD_PROJECT" -auto-approve)
```

### **セキュリティについて**

セキュリティについても Firestore と同様、クライアントから直接操作する関係上、設定が必須となります。

Cloud Storage for Firebase でも**セキュリティルール**を利用してセキュリティを確保します。また Terraform で設定済みです。

今回は Firebase Authentication でログインしたユーザーが、**Cloud Storage 上の自分専用のフォルダ配下にのみ書き込み、読み込みができる**ようにしています。

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

ここで `https://console.〜` の URL をクリックすると、リアルタイムのコンテナビルドログを確認できます。

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

生成 AI 処理アプリケーションは Cloud SQL、Vertex AI などのサービスへのアクセス権限が必要です。

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
SUBSCRIPTIONS=$(gcloud pubsub subscriptions list --format json | jq -r '.[].name')
for SUBSCRIPTION in $SUBSCRIPTIONS
do gcloud pubsub subscriptions add-iam-policy-binding $SUBSCRIPTION \
    --member="serviceAccount:service-$PROJECT_NUMBER@gcp-sa-pubsub.iam.gserviceaccount.com" \
    --role="roles/pubsub.subscriber"
done
```

### **3. デッドレタートピックの設定、サブスクリプションの確認応答時間の修正**

```bash
SUBSCRIPTIONS=$(gcloud pubsub subscriptions list --format json | jq -r '.[].name')
for SUBSCRIPTION in $SUBSCRIPTIONS
do gcloud pubsub subscriptions update $SUBSCRIPTION \
    --ack-deadline 300 \
    --dead-letter-topic genai-backend-dead-letter
done
```

## **ソースデータに基づいた回答生成**

ソースデータに基づいた回答生成は RAG というテクニックを [LlamaIndex on Vertex AI for RAG](https://cloud.google.com/vertex-ai/generative-ai/docs/llamaindex-on-vertexai) を利用して実現しています。

ここでは具体的なソースコードを見ながら、詳細な処理を確認します。

RAG は一般的に大きくデータを準備する前処理と、質問への回答を生成する処理の 2 つに分かれています。

データを準備する前処理は以下の手順で行われます。

1. データの取り込み
1. データの変換
1. エンべディング化
1. データのインデックス化

上記の一連の手続きがソースコードでは<walkthrough-editor-select-line filePath="./next-tokyo-assets/2024/genai-app-patterns/src/genai-backend/main.py" startLine="113" endLine="119" startCharacterOffset="4" endCharacterOffset="5">こちら</walkthrough-editor-select-line>に該当します。

質問への回答生成は以下の手順で行われ、ソースコードの該当箇所を示します。

1. <walkthrough-editor-select-line filePath="./next-tokyo-assets/2024/genai-app-patterns/src/genai-backend/main.py" startLine="171" endLine="184" startCharacterOffset="4" endCharacterOffset="5">質問に関連するデータをインデックスから取得</walkthrough-editor-select-line>
1. <walkthrough-editor-select-line filePath="./next-tokyo-assets/2024/genai-app-patterns/src/genai-backend/main.py" startLine="186" endLine="190" startCharacterOffset="4" endCharacterOffset="5">インデックスから取得したデータと質問を合わせて回答を生成</walkthrough-editor-select-line>

## **マルチターンの質問回答**

過去の質問内容、回答内容を踏まえた質問回答 (マルチターンの質問回答) を生成するには、**生成 AI に対して現在の質問に加えて、今までのやり取りも合わせて送る**必要があります。

つまり生成 AI は今までのやり取りを記憶しているわけではなく、プログラム側で対応が必要になります。

今回のプログラムでは Firestore に質問と回答の履歴を持つようにし、質問を投げたときに履歴すべてを質問に合わせて送るようにしています。

具体的な処理部分を以下に示します。

- <walkthrough-editor-select-line filePath="./next-tokyo-assets/2024/genai-app-patterns/src/genai-backend/main.py" startLine="192" endLine="198" startCharacterOffset="4" endCharacterOffset="5">過去の履歴を取得</walkthrough-editor-select-line>
- <walkthrough-editor-select-line filePath="./next-tokyo-assets/2024/genai-app-patterns/src/genai-backend/main.py" startLine="206" endLine="206" startCharacterOffset="8" endCharacterOffset="65">過去の履歴を含め質問を送信</walkthrough-editor-select-line>

## **AI organizer の試用**

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
1. 少し待つと読み込み処理が完了し、ロード中マークが消えます。

**サンプル PDF 一覧**

- [Cloud Run](https://storage.googleapis.com/genai-handson-20230929/CloudRun.pdf)
- [Cloud SQL](https://storage.googleapis.com/genai-handson-20230929/CloudSQL.pdf)
- [Cloud Storage for Firebase](https://storage.googleapis.com/genai-handson-20230929/CloudStorageforFirebase.pdf)
- [Firebase Authentication](https://storage.googleapis.com/genai-handson-20230929/FirebaseAuthentication.pdf)
- [Firestore](https://storage.googleapis.com/genai-handson-20230929/Firestore.pdf)
- [Palm API と LangChain の連携](https://storage.googleapis.com/genai-handson-20230929/PalmAPIAndLangChain.pdf)

### **5. ソースに関連する質問**

- アップロードしたソースのチェックボックスをチェックし、最下部の質問バーから質問を入力します。

うまくいくと、アップロードしたファイルの内容をベースに回答が生成されます。

### **6. 気に入った回答を保存する**

気に入った回答の右上にあるピンボタンをクリックすると、メモとして保存することが可能です。

### **7. 色々活用してみる**

手持ちの PDF などをアップロードし、回答に利用したい PDF を選択、質問を繰り返してどのような回答になるかを体験してみてください。

### **8. ログアウトする**

画面の右上のアイコン (扉からでていくマーク) をクリックするとログアウトが可能です。

### **9. 新規ユーザーを作成し、データが別管理になっていることを確認する**

新しいユーザーを作成し、動作を確認してみてください。

ユーザーごとにデータが分けられて管理されており、先程アップロードしたデータは見えないことがわかります。

## **Congratulations!**

<walkthrough-conclusion-trophy></walkthrough-conclusion-trophy>

これにて**丸わかり！生成 AI アプリケーション開発パターン**は完了です。

Qwiklabs に戻り、`ラボを終了` ボタンをクリックし、ハンズオンを終了します。
