# 生成 AI で作る商品カタログと、Google の検索技術で作る商品検索サービス

## このハンズオンについて

このハンズオンでは、Google の生成 AI モデル「Gemini」のマルチモーダル機能を使った Product Enrichment と、Vertex AI Search for Retail を使った商品情報のセマンティック検索を体験できます。

このハンズオンを通して、次の機能の使い方を学習できます。

- Gemini API を使ったマルチモーダル推論
- Workflows の一連のステップのオーケストレーション
- Cloud Run サービスの並列処理
- BigQuery へのデータインポート
- Vertex AI Search for Retail へのデータインポート
- Vertex AI Search for Retail の検索の評価

## プロジェクトの課金が有効化されていることを確認する

まず初めに、Google Cloud プロジェクトの課金が有効になっているか確認しましょう。

```bash
gcloud beta billing projects describe ${GOOGLE_CLOUD_PROJECT} | grep billingEnabled
```

**Cloud Shell の承認** という確認メッセージが出た場合は **承認** をクリックします。

出力結果の `billingEnabled` が **true** になっていることを確認してください。**false** の場合は、こちらのプロジェクトではハンズオンが進められません。別途、課金を有効化したプロジェクトを用意し、本ページの #1 の手順からやり直してください。

## 環境準備

<walkthrough-tutorial-duration duration=10></walkthrough-tutorial-duration>

最初に、ハンズオンを進めるための環境準備を行います。

下記の設定を進めていきます。

- gcloud コマンドラインツールの設定
- Google Cloud 機能（API）有効化の設定

## **gcloud コマンドラインツール**

Google Cloud は、コマンドライン（CLI）、GUI から操作が可能です。ハンズオンでは主に CLI を使い作業を行いますが、GUI で確認する URL もあわせて掲載します。

### **1. gcloud コマンドラインツールとは?**

gcloud コマンドライン インターフェースは、Google Cloud でメインとなる CLI ツールです。このツールを使用すると、コマンドラインから、またはスクリプトや他の自動化により、多くの一般的なプラットフォーム タスクを実行できます。

たとえば、gcloud CLI を使用して、以下のようなものを作成、管理できます。

- Google Compute Engine 仮想マシン
- Google Kubernetes Engine クラスタ
- Google Cloud SQL インスタンス

**ヒント**: gcloud コマンドラインツールについての詳細は[こちら](https://cloud.google.com/sdk/gcloud?hl=ja)をご参照ください。

### **2. gcloud のデフォルト設定**

gcloud CLI に、デフォルトの設定を行っておきます。この設定を行っておくことで、よく行う設定（リージョン、プロジェクトの指定など）をコマンドを実行するたびに指定せずに済みます。

```bash
gcloud config set project ${GOOGLE_CLOUD_PROJECT}
gcloud config set run/region asia-northeast1
gcloud config set workflows/location asia-northeast1
```

### **3. 使用するサービスの API の有効化**

Google Cloud では、プロジェクトで使用するサービスの API を一つずつ有効化する必要があります。Cloud Run や BigQuery、Vertex AI などの API を gcloud コマンドで有効化します。

```bash
gcloud services enable bigquery.googleapis.com
gcloud services enable aiplatform.googleapis.com
gcloud services enable run.googleapis.com 
gcloud services enable cloudbuild.googleapis.com
gcloud services enable artifactregistry.googleapis.com
gcloud services enable workflows.googleapis.com
gcloud services enable cloudresourcemanager.googleapis.com
```

## 商品画像ファイルを Cloud Storage にアップロードする

商品画像ファイルは、共通でアクセスできる Cloud Storage バケットにあらかじめ用意してあります。

自分の Google Cloud プロジェクトで Cloud Storage バケットを新規作成し、商品画像ファイルをコピーします。

まずは、専用の Cloud Storage バケットを新規作成します。

```bash
gcloud storage buckets create gs://products-${GOOGLE_CLOUD_PROJECT} --location asia-northeast1
```

次に、商品画像がすでにアップロードされている Cloud Storage バケットから、新規作成した Cloud Storage バケットに画像ファイルをコピーします。

```bash
gcloud storage cp gs://next-tokyo-24-handson-products/* gs://products-${GOOGLE_CLOUD_PROJECT}
```

画像ファイルがアップロードできているか確認しましょう。

```bash
gcloud storage ls gs://products-${GOOGLE_CLOUD_PROJECT}
```

Cloud Storage コンソールから、実際の画像ファイルを確認することもできます。

## 商品データを管理する BigQuery テーブルを作成する

JSON ファイルのデータから、BigQuery テーブルを作成します。

まず、BigQuery データセットを作成します。

```bash
bq mk --dataset ${GOOGLE_CLOUD_PROJECT}:catalog
```

データセットが作成できたら、そのデータセットに新規テーブルを作成します。スキーマ定義は予め用意してある `schema.json` を使用します。このスキーマには、このあと Gemini を使って生成するタイトルや説明などのカラムが定義されています。

```bash
bq mk --table ${GOOGLE_CLOUD_PROJECT}:catalog.products ./schema.json
```

## Cloud Run サービスを作成する

画像から商品情報を生成するリクエストを送る、並列処理させるタスクを Cloud Run サービスを使って構築します。

リポジトリ内の `catalog-enrichment-job` が Cloud Run サービスで使用するアプリケーション コードです。

```bash
cd catalog-enrichment-job
```

処理を行うサービスは Gemini の呼び出しと BigQuery テーブルの読み書きを行います。そのため、サービスに割り当てるサービスアカウントを作成し、BigQuery と Vertex AI の権限を付与します。

サービスアカウントの作成と権限の付与は gcloud コマンドから行うことができます。

```bash
gcloud iam service-accounts create catalog-enrichment-job-sa
```

BigQuery のテーブルへの読み書きができる権限と Vertex AI の Gemini が呼び出せる権限を付与します。

```bash
gcloud projects add-iam-policy-binding $GOOGLE_CLOUD_PROJECT \
     --member "serviceAccount:catalog-enrichment-job-sa@${GOOGLE_CLOUD_PROJECT}.iam.gserviceaccount.com" \
     --role "roles/bigquery.dataEditor"

gcloud projects add-iam-policy-binding $GOOGLE_CLOUD_PROJECT \
     --member "serviceAccount:catalog-enrichment-job-sa@${GOOGLE_CLOUD_PROJECT}.iam.gserviceaccount.com" \
     --role "roles/bigquery.jobUser"

gcloud projects add-iam-policy-binding $GOOGLE_CLOUD_PROJECT \
     --member "serviceAccount:catalog-enrichment-job-sa@${GOOGLE_CLOUD_PROJECT}.iam.gserviceaccount.com" \
     --role "roles/aiplatform.user"

gcloud projects add-iam-policy-binding $GOOGLE_CLOUD_PROJECT \
     --member "serviceAccount:catalog-enrichment-job-sa@${GOOGLE_CLOUD_PROJECT}.iam.gserviceaccount.com" \
     --role "roles/storage.objectViewer"
```

次に、Cloud Run サービスを gcloud コマンドで作成します。

`gcloud run deploy` コマンドを使用することで、ソースコードのアップロード、コンテナイメージのビルド、コンテナイメージのプッシュ、そして Cloud Run サービスの作成を一度に行うことができます。

```bash
gcloud run deploy catalog-enrichment-job \
  --source . \
  --service-account "catalog-enrichment-job-sa@${GOOGLE_CLOUD_PROJECT}.iam.gserviceaccount.com" \
  --set-env-vars "PROJECT_ID=${GOOGLE_CLOUD_PROJECT}" \
  --set-env-vars "REGION=asia-northeast1" \
  --set-env-vars "TABLE_ID=${GOOGLE_CLOUD_PROJECT}.products.products" \
  --set-env-vars "BUCKET=products-${GOOGLE_CLOUD_PROJECT}" \
  --allow-unauthenticated \
  --port 3000
```

デプロイ後、画面に表示される URL を環境変数にセットしておきます。

```bash
export URL="<Cloud Run の URL>"
```

デプロイが失敗する場合は、Cloud Build に割り当てられているサービスアカウントの権限が不足していることが考えられます。その場合は次のコマンドを実行し、Cloud Storage 管理者権限を付与してから再実行してみてください。

```bash
PROJECT_NUMBER=$(gcloud projects list --filter="$(gcloud config get-value project)" --format="value(PROJECT_NUMBER)")
gcloud projects add-iam-policy-binding $GOOGLE_CLOUD_PROJECT \
     --member "serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
     --role "roles/storage.admin"
```

Artifact Registry をプロジェクトで一度も使用したことがない場合、次のメッセージが表示されることがあります。`Y` で続行してください。

```
Deploying from source requires an Artifact Registry Docker repository to store built containers. A repository named [cloud-run-source-deploy] in region [asia-northeast1] will be 
created.

Do you want to continue (Y/n)?
```

Cloud Run サービスのコンソールで、サービスが作成されていることが確認できます。

## Workflows のワークフローを作成する

Workflows では、次のステップを順に処理するワークフローを作成します。

1. Cloud Storage バケットのオブジェクト リストを取得する
2. Cloud Run サービスで商品ごとにリクエストする

まず、ワークフローに割り当てるサービスアカウントを作成します。

```bash
gcloud iam service-accounts create catalog-enrichment-workflow-sa
```

サービスアカウントには、Cloud Storage バケットの読み取り権限の実行権限を付与します。

```bash
gcloud projects add-iam-policy-binding $GOOGLE_CLOUD_PROJECT \
     --member "serviceAccount:catalog-enrichment-workflow-sa@$GOOGLE_CLOUD_PROJECT.iam.gserviceaccount.com" \
     --role "roles/storage.objectViewer"
```

ワークフローの定義は `workflow.yaml` に書かれています。この定義を使って、gcloud コマンドでワークフローを作成します。

カレントが `catalog-enrichment-job` ディレクトリの場合は、一階層上のディレクトリに移動してから実行します。

```bash
cd ../
```

次のコマンドで、ワークフローを作成します。

```bash
gcloud workflows deploy catalog-enrichment-workflow \
  --source=workflow.yaml \
  --service-account=catalog-enrichment-workflow-sa@${GOOGLE_CLOUD_PROJECT}.iam.gserviceaccount.com \
  --set-env-vars BUCKET=products-${GOOGLE_CLOUD_PROJECT},URL=${URL}
```

作成したら、ワークフローを実行します。

```bash
gcloud workflows run catalog-enrichment-workflow
```

BigQuery にインポート済みの、全ての商品に対してタイトルや説明文が生成されます。

注 : ワークフローの実行でエラーが出る場合は、サービスアカウントへの実行権限の付与に時間がかかっている可能性があります。エラーが出た場合は数分待ってから再実行してみてください。

ワークフローの実行が完了したら、コンソールでワークフローが問題なく完了していることを確認しましょう。

正常に完了していれば、BigQuery テーブルに生成された商品情報が保存されています。BigQuery コンソールから確認してみましょう。

## Vertex AI Search for Retail の利用を開始する

次に Vertex AI Search for Retail に商品データをインポートし、検索を試してみましょう。

Vertex AI Search for Retail が Google Cloud プロジェクトで使用できるように設定します。Vertex AI Search for Retail の利用を開始するには、Vertex AI Search for Retail コンソールからデータ利用規約に同意する必要があります。

1. Google Cloud コンソールで [小売業向け Vertex AI Search] ページに移動します。ナビゲーションで見つからない場合は、検索ボックスに「小売業向け Vertex AI Search」と入力します。
2. [Vertex AI Search for Retail を設定する] ページで、[API を有効にする] をクリックします。
3. Vertex AI Search for Retail と Recommendations AI が オン と表示されたら、[続行] をクリックします。
4. Vertex AI Search for Industry のデータ使用条件を確認します。データ使用条件に同意した場合は、[承諾] をクリックします。有効化が完了するまでには 30 秒程度かかります。完了したら、[続行] をクリックします。
5. 検索機能と閲覧機能の有効化で [オンにする] をクリックします。
6. 最後に [開始] をクリックします。

## Vertex AI Search for Retail にデータをインポートする

Vertex AI Search for Retail に、BigQuery テーブルに作成済みの商品カタログデータをインポートします。

Vertex AI Search for Retail では、インポートすることができる商品カタログデータのスキーマが定義されています。そこでまずはじめに、現在保存している BigQuery テーブルを Vertex AI Search for Retail 用のデータに変換します。変換には BigQuery のビューの機能を利用し、実際のデータのコピーを行わずにインポートできるようにします。

ビューは `bq` コマンドから作成できます。

```bash
bq mk \
  --use_legacy_sql=false \
  --view "SELECT id, title, categories, description, [STRUCT(CONCAT(\"https://storage.cloud.google.com/products-${GOOGLE_CLOUD_PROJECT}/\", image) as uri)] as images FROM \`${GOOGLE_CLOUD_PROJECT}.catalog.products\`" \
  "${GOOGLE_CLOUD_PROJECT}:catalog.products_view"
```

Vertex AI Search for Retail に商品カタログデータをインポートします。Vertex AI Search for Retail の API はサービスアカウントからしか呼び出せないため、サービスアカウントを作成し、サービスアカウントからインポート API を呼び出します。

`retail-api-client-sa` という名前のサービスアカウントを作成します。

```bash
gcloud iam service-accounts create retail-api-client-sa
```

`retail-api-client-sa` サービスアカウントには `roles/retail.editor` のロールを付与します。

```bash
gcloud projects add-iam-policy-binding $GOOGLE_CLOUD_PROJECT \
     --member "serviceAccount:retail-api-client-sa@${GOOGLE_CLOUD_PROJECT}.iam.gserviceaccount.com" \
     --role "roles/bigquery.dataEditor"

gcloud projects add-iam-policy-binding $GOOGLE_CLOUD_PROJECT \
     --member "serviceAccount:retail-api-client-sa@${GOOGLE_CLOUD_PROJECT}.iam.gserviceaccount.com" \
     --role "roles/retail.editor"
```

サービスアカウントの認証情報をダウンロードし、`gcloud` コマンドが認証情報を使って実行されるように設定します。URL が表示されるので、アクセスし画面の指示通りに認証を行います。

```bash
gcloud auth application-default login --impersonate-service-account retail-api-client-sa@${GOOGLE_CLOUD_PROJECT}.iam.gserviceaccount.com
```

次のコマンドで、サービスアカウントのアクセストークンを取得し、そのアクセストークンを使ってインポート API を呼び出します。

```bash
curl --request POST \
  "https://retail.googleapis.com/v2/projects/${GOOGLE_CLOUD_PROJECT}/locations/global/catalogs/default_catalog/branches/default_branch/products:import" \
  --header "Authorization: Bearer $(gcloud auth application-default print-access-token --impersonate-service-account retail-api-client-sa@${GOOGLE_CLOUD_PROJECT}.iam.gserviceaccount.com)" \
  --header 'Accept: application/json' \
  --header 'Content-Type: application/json' \
  --data "{\"inputConfig\":{\"bigQuerySource\":{\"tableId\":\"products_view\",\"datasetId\":\"catalog\",\"projectId\":\"${GOOGLE_CLOUD_PROJECT}\"}}}" \
  --compressed
```

## Vertex AI Search for Retail の検索を評価する

Vertex AI Search for Retail のコンソールから、キーワードによる検索結果を試すことができます。どのように動作するか、実際に試してみましょう。

1. Vertex AI Search for Retail (小売向け検索) コンソールの [評価] をクリックします。
2. [検索] タブをクリックします。
3. 任意の検索クエリを入力し、[検索プレビュー] をクリックします。

様々な検索キーワードで検索を試してみてください。

## お疲れ様でした

以上でハンズオンは終了です。お疲れ様でした。