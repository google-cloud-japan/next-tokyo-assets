# ハンズオン: BigQuery と Gemini で始める顧客の声分析と可視化

## ハンズオンの概要

あなたは、東京と横浜に店舗を持つ小売チェーン Next Drug の CS 担当者です。

Next Drug は、顧客満足度を向上させるために、店舗に来店した顧客からアンケートを収集しています。しかし、アンケートの回答は CSV 形式で保存されており、そのデータ量は膨大です。

あなたは、この大量のアンケートデータを効率的に分析し、具体的なサービス改善につなげたいと考えています。

そのために、あなたは BigQuery と Gemini を活用することで、これらの課題を解決できると考えました。

### このラボの内容
* CSV 形式の店舗データ、アンケートデータを BigQuery にインポートする
* Gemini in BigQuery を用いてデータを理解する
* BigQueryML と Gemini を用いてアンケートデータを分析する
* Data Canvas を用いてクイックにデータを可視化する
* Looker Studio を用いてダッシュボードを作成する


## ハンズオンの開始
<walkthrough-tutorial-duration duration=5></walkthrough-tutorial-duration>
まずはハンズオンに利用するファイルをダウンロードします。
<walkthrough-info-message>既に実施済の方はこの手順をスキップできます。</walkthrough-info-message>

1. Cloud Shell 
<walkthrough-cloud-shell-icon></walkthrough-cloud-shell-icon> を開きます。

2. 次のコマンドを実行してハンズオン資材をダウンロードし、チュートリアルを開きます。
```bash
git clone https://github.com/google-cloud-japan/next-tokyo-assets.git
cd ~/next-tokyo-assets/2024/bq/
teachme tutorial.md
```

## Google Cloud プロジェクトの設定
次に、ターミナルの環境変数にプロジェクトIDを設定します。
```bash
export PROJECT_ID=$(gcloud config list --format 'value(core.project)')
```
<walkthrough-info-message>**Tips:** コードボックスの横にあるボタンをクリックすることで、クリップボードへのコピーおよび Cloud Shell へのコピーが簡単に行えます。</walkthrough-info-message>

次に、このハンズオンで利用するAPIを有効化します。

<walkthrough-enable-apis apis=
  "bigquery.googleapis.com, bigquerydatatransfer.googleapis.com, cloudaicompanion.googleapis.com, aiplatform.googleapis.com, dataplex.googleapis.com">
</walkthrough-enable-apis>

## **[シナリオ1] CSV 形式の店舗データ、アンケートデータを BigQuery にインポートする**

<walkthrough-tutorial-duration duration=15></walkthrough-tutorial-duration>

あなたはまず、Next Drug の各店舗から送られてきた CSV 形式のデータを扱います。

店舗データには店舗名、住所などが、売上データには商品 ID、売上金額、販売日時などが、アンケートデータには店舗 ID と定性的なコメントが含まれています。

これらのデータを手作業で分析するのは困難なため、あなたは BigQuery にデータをインポートすることにしました。BigQuery のインターフェースを使ってそれぞれの CSV ファイルをインポートし、分析の準備を整えます。

## BigQuery への CSV ファイルのインポート

ここでは bq コマンドを用いて CSV ファイルを BigQuery にインポートします。

1. 次のコマンドを実行して、インポートする 4 つの CSV ファイルを確認します。
```bash
ls -l *.csv
```

2. ファイルのインポート先となる BigQuery データセットを作成します。データセットとは、テーブルなどのリソースを格納するコンテナです。
```bash
bq mk --location=us-central1 --dataset ${PROJECT_ID}:next_drug
```

3. 4 つの CSV ファイルを作成したインポートし、データセット内に 4 つのテーブルを作成します。
```bash
bq load --location=us-central1 --autodetect --replace --source_format=CSV ${PROJECT_ID}:next_drug.store ./store.csv
bq load --location=us-central1 --autodetect --replace --source_format=CSV ${PROJECT_ID}:next_drug.order ./order.csv
bq load --location=us-central1 --autodetect --replace --source_format=CSV ${PROJECT_ID}:next_drug.order_items ./order_items.csv
bq load --location=us-central1 --autodetect --replace --source_format=CSV ${PROJECT_ID}:next_drug.customer_voice ./customer_voice.csv

```

CSV ファイルを BigQuery にインポートすることができました。

## 作成した BigQuery データセットの確認

ここからはより直感的に理解しやすいよう Cloud Console 上で操作を行いますので、Cloud Shell は閉じて構いません。

1. ナビゲーションメニュー <walkthrough-nav-menu-icon></walkthrough-nav-menu-icon> から [**BigQuery**] に移動します。

2. エクスプローラペインの **自身の プロジェクト ID** の下に、データセット `next_drug` が作成されていることを確認します。

3. `next_drug` データセットの下にある `store` テーブルを選択します。

4. <walkthrough-spotlight-pointer cssSelector="[instrumentationid=bq-table-preview-tab]" single="true">[**プレビュー**]</walkthrough-spotlight-pointer> をクリックします。

3つの店舗のデータが正しく取り込まれていることが分かります。

同様に `customer_voice` テーブルもプレビューを確認します。各店舗に来店した顧客のアンケートデータが取り込まれていることが分かります。


## 作成した BigQuery データセットの確認 (続き)
続けて、`order` テーブルと `order_items` テーブルのデータを確認します。
2 つのテーブルは各店舗での販売データが格納されている親子関係のテーブルです。

### **order テーブル**
1. エクスプローラーペインで `next_drug` データセットの下にある `order` テーブルを選択します。

2. スキーマの 3 つの行をすべて選択し、[**探索**] をクリックします。
各フィールドにどんな値が含まれているかが表示されます。

* `order_id` はレコードごとに異なるユニークなキーです。
* `store_id` は各店舗を示す ID です。
* `order_timestamp` は店舗での販売日時です。

### **order_items テーブル**
3. エクスプローラーペインで `next_drug` データセットの下にある `order_items` テーブルを選択します。

4. スキーマの `category`, `item` と `total_price` を選択し、[**探索**] をクリックします。
各フィールドにどんな値が含まれているかが表示されます。

* `category` は販売された商品のカテゴリです。
* `item` は販売された商品の名前です。
* `total_price` は商品の販売金額です。

BigQuery へインポートしたデータを確認することができました。

## **[シナリオ2] Gemini in BigQuery を用いてデータを理解する**

<walkthrough-tutorial-duration duration=15></walkthrough-tutorial-duration>

膨大なデータの中身を確認するために、Gemini in BigQuery を活用します。「2024 年 7 月の各店舗の売上金額は?」といった質問を自然言語で投げかけると、Gemini が自動的に SQL クエリを生成し、結果を表示してくれます。これにより、データの全体像を素早く把握し、分析の方向性を定めることができます。

<!-- TODO:Data Insights が public になったら追加 -->

## BigQuery で簡単なクエリを実行

まずは、Gemini を使わずに SQL クエリを実行する方法を試します。

1. <walkthrough-spotlight-pointer cssSelector="[instrumentationid=bq-sql-code-editor] button[name=addTabButton]" single="true">[**SQL クエリを作成**] アイコン</walkthrough-spotlight-pointer> をクリックして、新しいタブを開きます。

2. 下記の SQL を入力し、[**実行**] をクリックして実行結果を確認します。
```SQL
SELECT
  COUNT(order_id) AS customer_total
FROM
  `next_drug.order`
WHERE
  DATE(order_timestamp) = '2024-07-31'
```

2024 年 7 月 31 日の来客数が表示されました。

次に、SQL クエリの結果を BigQuery 内で保存する方法を学びます。

3. 実行結果を新しいテーブル `daily_customer` に保存するには、同じタブで下記の SQL を実行します。

```SQL
CREATE OR REPLACE TABLE `next_drug.daily_customer` AS
SELECT
  store,
  lat_long,
  COUNT(order_id) AS customer_total
FROM
  `next_drug.order` oi
JOIN
  `next_drug.store` s
ON
  oi.store_id = s.store_id
WHERE
  DATE(order_timestamp) = '2024-07-31'
GROUP BY
  1,2
```

エクスプローラーペインの **プロジェクト ID** > `next_drug` の下に新しいテーブル `daily_customer` が作成されていることが確認できます。

## Gemini で SQL クエリを生成

次に、Gemini を用いて SQL クエリを生成します。

<!-- Geminiの有効化ができてなかったら、以下の手順を追加

まず、Gemini in BigQuery を有効化します。

1. クエリエディタの横にある <walkthrough-spotlight-pointer cssSelector="[instrumentationid=bq-sql-code-editor] button#_1rif_Gemini" single="true">[**Gemini**] アイコン</walkthrough-spotlight-pointer> にマウスカーソルを合わせ、表示されたツールチップの [**続行**] をクリックします。

2. [**Geminiを有効にする**]ペインで、Trusted Tester プログラムに関する利用規約への同意にチェックを入れ、[**次へ**] をクリックします。

3. [**Cloud AI Companion API**] が無効になっている場合は [**有効にする**] をクリックし、[**閉じる**] をクリックします。
-->

1. <walkthrough-spotlight-pointer cssSelector="[instrumentationid=bq-sql-code-editor] button[name=addTabButton]" single="true">[**SQL クエリを作成**] アイコン</walkthrough-spotlight-pointer> をクリックして、新しいタブを開きます。

2. <walkthrough-spotlight-pointer cssSelector="sqe-duet-trigger-overlay" single="true">[**コーディングをサポート**]アイコン</walkthrough-spotlight-pointer> をクリックするか、Ctrl + Shift + P を入力して、[**コーディングをサポート**]ツールを開きます。

3. 次のプロンプトを入力します。
```
next_drug データセットから、販売金額トップ 10 の商品とそのカテゴリを調べるクエリを書いて
```

4. [**生成**] をクリックします。
  Gemini は、次のような SQL クエリを生成します。
```terminal
-- next_drug データセットから、販売金額トップ 10 の商品とそのカテゴリを調べるクエリを書いて
SELECT
    oi.item,
    oi.category,
    SUM(oi.total_price) AS total_sales
  FROM
    `next_drug.order_items` AS oi
  GROUP BY 1, 2
ORDER BY
  total_sales DESC
LIMIT 10;
```

<walkthrough-info-message>**注:** Gemini は、同じプロンプトに対して異なる SQL クエリを提案する場合があります。必要に応じてクエリを修正してください。</walkthrough-info-message>

5. 生成された SQL クエリを受け入れるには、[**挿入**] をクリックして、クエリエディタにステートメントを挿入します。[**実行**] をクリックして、提案された SQL クエリを実行します。

6. 実行したクエリを保存して、チームへの共有や次回に再利用することができます。 [**保存**] をクリックし、続いて [**クエリを保存**] をクリックします。

7. [**名前**] に `販売トップ10` と入力し、[**リージョン**] に `us-central1` を選択し、[**保存**] をクリックします。

8. 保存されたクエリはエクスプローラペインの **プロジェクト ID** > [**クエリ**] の下で確認ができます。

Gemini で SQL クエリを生成する方法を学びました。

### **チャレンジ問題**
<walkthrough-spotlight-pointer cssSelector="[instrumentationid=bq-sql-code-editor] button[name=addTabButton]" single="true">[**SQL クエリを作成**] アイコン</walkthrough-spotlight-pointer> をクリックして新しいタブを開き、自由に SQL クエリの生成を試してみましょう。

* 最も販売数が多い商品カテゴリは？
* 各店舗で最も来店が多い時間帯は？


## BigQueryでクエリの定期実行を設定
次に、定期的にクエリを実行するスケジュールの作成をします。

1. エクスプローラーペインから **プロジェクト ID** > [**クエリ**] > `販売トップ10` を選択します。
2. クエリを以下のように修正し、[**クエリを保存**] をクリックします。1行目を追加し、実行結果を新しいテーブル `top10_items` に保存するようにしています。
```sql
CREATE OR REPLACE TABLE `next_drug.top10_items` AS
SELECT
    oi.item,
    oi.category,
    SUM(oi.total_price) AS total_sales
  FROM
    `next_drug.order_items` AS oi
  GROUP BY 1, 2
ORDER BY
  total_sales DESC
LIMIT 10;
```

3. [**スケジュール**] をクリックします。
4. **新たにスケジュールされたクエリ** ペインで次のとおり入力します。

フィールド | 値
---------------- | ----------------
クエリの名前 | `販売トップ10`
繰り返しの頻度 | 日
時刻 | `01:00`
すぐに開始 | 選択する
ロケーションタイプ | リージョン
リージョン | `us-central1`

5. 他はデフォルトのまま [**保存**] をクリックし、スケジュールを保存します。認証を求められた場合は、ハンズオン用のユーザーを選んで認証します。
6. すぐに開始 を選択したため、エクスプローラーペインの **プロジェクト ID** > `next_drug` の下に新しいテーブル `top10_items` が作成されていることが確認できます。
7. スケジュールされたクエリの実行結果を、ナビゲーションペインの **スケジュールされたクエリ**  から確認します。

BigQuery のデータに対するクエリの定期実行の方法を学びました。


## **[シナリオ3] BigQueryML と Gemini を用いてアンケートデータを分析する**

<walkthrough-tutorial-duration duration=15></walkthrough-tutorial-duration>

顧客満足度を向上させるためには、アンケートデータの詳細な分析が必要です。BigQueryML と Gemini を組み合わせることで、アンケートの自由記述回答を分析し、顧客の不満や要望を抽出します。例えば、「品揃えが悪い」「レジ待ち時間が長い」といった不満や、「オーガニック商品の拡充」「セルフレジの導入」といった要望を特定することができます。

## BigQueryからVertex AIへの接続を作成
<walkthrough-tutorial-duration duration=15></walkthrough-tutorial-duration>
まず、BigQuery から Vertex AI への接続を作成します。

1. 接続を作成するには、エクスプローラペインの [**+追加**] をクリックし、続いて [**外部データソースへの接続**] をクリックします。
2. **外部データソース** ペインで、次の情報を入力します。

フィールド | 値
--- | ---
接続タイプ | **Vertex AI リモートモデル、リモート関数、BigLake（Cloud リソース）**
接続 ID | `gemini-connect`
ロケーションタイプ | **リージョン**
リージョン | `us-central1`

3. [**接続を作成**] をクリックします。
4. [**接続へ移動**] をクリックします。
5. [**接続情報**] ペインで、次の手順で使用する **サービス アカウント ID** をコピーします。(`bqcx-`から始まる文字列)

## Vertex AIへの接続で用いるサービスアカウントにアクセス権限を付与

次に、作成した接続で用いるサービスアカウントにアクセス権限 (IAM) を付与します。

1. ナビゲーションメニュー <walkthrough-nav-menu-icon></walkthrough-nav-menu-icon> から [**IAMと管理**] > [**IAM**] に移動します。

2. [**アクセス権を付与**] をクリックします。

3. [**新しいプリンシパル**] に、前の手順でコピーしたアカウント ID を入力します。

4. [**ロールを選択**] をクリックし、[**Vertex AI**] > [**Vertex AI ユーザー**] を選択します。

5. [**保存**] をクリックし、アクセス権を付与します。

## BigQuery から生成 AI モデル Gemini へ接続
続いて、作成した接続を用いて BigQuery から生成 AI モデル Gemini へ接続します。

1. ナビゲーションメニュー <walkthrough-nav-menu-icon></walkthrough-nav-menu-icon> から [**BigQuery**] に移動します。

2. <walkthrough-spotlight-pointer cssSelector="[instrumentationid=bq-sql-code-editor] button[name=addTabButton]" single="true">[**SQL クエリを作成**] アイコン</walkthrough-spotlight-pointer> をクリックして新しいタブを開き、以下の SQL を実行します。
```sql
CREATE OR REPLACE MODEL next_drug.gemini_model
  REMOTE WITH CONNECTION `us-central1.gemini-connect`
  OPTIONS(ENDPOINT = 'gemini-1.5-flash')
```
ここでは、生成 AI モデルの Gemini Flash を指定しました。

3. 同じタブで以下の SQL を実行し、Gemini からのレスポンスを確認します。
```sql
SELECT JSON_VALUE(ml_generate_text_result.candidates[0].content.parts[0].text) as response
FROM ML.GENERATE_TEXT(
    MODEL next_drug.gemini_model,
    (SELECT 'Google Cloud Next について教えてください' AS prompt),
    STRUCT(1000 as max_output_tokens, 0.2 as temperature)
  )
```
<walkthrough-info-message>**注:** 前ステップで付与したアクセス権限が反映されるまでに時間がかかり、SQL クエリの実行時に Permission エラーが発生する場合があります。数分待ってから再度 SQL クエリを実行してください。</walkthrough-info-message>


## Customer voice データの感情分析
ここからはテーブルに保存したアンケートデータを分析していきます。まずは、アンケートデータの内容をプレビューで確認しましょう。

1. エクスプローラーペインから **プロジェクト ID** > `next_drug` > `customer_voice` テーブルを選択し、[**プレビュー**] をクリックします。

次に、アンケートデータを 1 レコードずつ Gemini に渡して、顧客の声がポジティブかネガティブかを判定するようなクエリを考えます。

2. <walkthrough-spotlight-pointer cssSelector="[instrumentationid=bq-sql-code-editor] button[name=addTabButton]" single="true">[**SQL クエリを作成**] アイコン</walkthrough-spotlight-pointer> をクリックし、次の SQL を入力して [**実行**] をクリックします。 
```sql
CREATE OR REPLACE TABLE
  next_drug.customer_voice_analyzed AS
SELECT
  timestamp,      
  customer_voice,
  store,
  JSON_VALUE(ml_generate_text_result.candidates[0].content.parts[0].text) AS sentiment
FROM
  ML.GENERATE_TEXT( MODEL next_drug.gemini_model,
    (
    SELECT
      CONCAT( 
        '次の[顧客の声]の感情分析を行い、[出力形式]に従って出力してください。¥n¥n', 
        '[出力形式]¥nNegative, Neutral, Positive のいずれか1つをプレーンテキストで出力。余計な情報は付加しないこと。¥n¥n', 
        '[顧客の声]¥n', 
        customer_voice ) AS prompt,
      timestamp,
      customer_voice,
      store
    FROM
      `next_drug.customer_voice` cv
    JOIN
      `next_drug.store` s
    ON
      cv.store_id = s.store_id ),
    STRUCT(1000 AS max_output_tokens,
      0.0 AS temperature) )
```
3. エクスプローラーペインで `next_drug` > `customer_voice_analyzed` を選択し、[**プレビュー**] をクリックして顧客の声の感情分析の結果を確認します。

## Customer voice データのトピック分析
テーブルに保存したアンケートデータを 1 レコードずつ Gemini に渡して、顧客の声のトピックを分析するようなクエリを考えましょう。

1. <walkthrough-spotlight-pointer cssSelector="[instrumentationid=bq-sql-code-editor] button[name=addTabButton]" single="true">[**SQL クエリを作成**] アイコン</walkthrough-spotlight-pointer> をクリックし、次の SQL を入力して [**実行**] をクリックします。 
```sql
CREATE OR REPLACE TABLE
  next_drug.customer_voice_analyzed AS
SELECT
  timestamp,
  customer_voice,
  store,
  sentiment,
  JSON_VALUE(ml_generate_text_result.candidates[0].content.parts[0].text) AS topic
FROM
  ML.GENERATE_TEXT( MODEL next_drug.gemini_model,
    (
    SELECT
      CONCAT( 
        '次の[顧客の声]を分類して、[出力形式]に従って出力してください。¥n¥n', 
        '[出力形式]¥n商品・品揃え、価格、スタッフ、店舗環境、その他、のいずれか1つをプレーンテキストで出力。余計な情報は付加しないこと。¥n¥n', 
        '[顧客の声]¥n', 
        customer_voice ) AS prompt,
      timestamp,
      customer_voice,
      store,
      sentiment
    FROM
      `next_drug.customer_voice_analyzed` cv ),
    STRUCT(1000 AS max_output_tokens,
      0.0 AS temperature) )
```
2. エクスプローラーペインで `next_drug` > `customer_voice_analyzed` を選択し、[**プレビュー**] をクリックして顧客の声の分類結果を確認します。

生成AIモデル Gemini を用いた顧客の声データの分析ができました。

## **[シナリオ4] Data Canvas を用いてクイックにデータを可視化する**

<walkthrough-tutorial-duration duration=15></walkthrough-tutorial-duration>

分析結果を理解するために、Data Canvas を使ってデータを可視化します。店舗別の売上を比較する棒グラフ、顧客属性と満足度の関係を示す散布図などを簡単に作成できます。これらの視覚的な表現は、分析結果を直感的に理解するのに役立ち、改善策の検討を促進します。

## Data Canvas を用いたデータの探索
ここでは、Data Canvas を用いてクイックにデータを可視化する方法を学びます。

1. <walkthrough-spotlight-pointer cssSelector="[instrumentationid=bq-sql-code-editor] button[aria-label='その他の設定項目']" single="true">▼ボタン</walkthrough-spotlight-pointer>
をクリックしてドロップダウンメニューを開き [**データキャンバス**] を選択します。
キャンバスを保存するリージョンを選択するダイアログが表示された場合は、`us-central1` を選択します。

2. テキストボックスに`顧客の声の分析結果を保存したテーブル`と入力して [**検索**] をクリックします。 

3. `customer_voice_analyzed` のテーブルを選択し、[**Add to Canvas**] をクリックします。

4. 追加された `customer_voice_analyzed` のセルにマウスカーソルを合わせ、[**クエリ**] をクリックします。

5. 追加された SQL のセルのテキストボックスに、以下のプロンプトを入力して SQL クエリを生成します。
```
store, sentiment ごとの件数を集計
```

Gemini は、次のような SQL クエリを生成します。
```terminal
# prompt: store, sentiment ごとの件数を集計

SELECT
  store,
  sentiment,
  COUNT(*) AS COUNT
FROM
  `next_drug.customer_voice_analyzed`
GROUP BY
  1,
  2;
```

<walkthrough-info-message>**注:** Gemini は、同じプロンプトに対して異なる SQL クエリを提案する場合があります。必要に応じてクエリを修正してください。</walkthrough-info-message>

6. [**実行**] をクリックし、[**クエリ結果**] が表示されることを確認します。

7. セルにマウスカーソルを合わせ、[**可視化**] をクリックし、[**棒グラフの作成**] を選択します。

店舗ごとの顧客の声の内訳を示す棒グラフが作成できました。


## Data Canvas におけるテーブルの結合

次に、複数のテーブルを結合してデータを探索する方法を学びます。

1. Data Canvas 右下の **+ ボタン (ノードを追加)** をクリックし、[**新しい検索**] を選択します。
2. テキストボックスに`store, order`と入力して [**検索**] をクリックします。
3. `store` と `order` と `order_items` の 3 テーブルを選択し、[**結合**] をクリックします。
4. 追加された結合セルのテキストボックスに、以下のプロンプトを入力して SQL クエリを生成します。
```
これらのデータソースを結合し、横浜店の売上金額を日ごとカテゴリごとに集計
```

Gemini は、次のような SQL クエリを生成します。
```terminal
# prompt: これらのデータソースを結合し、横浜店の売上金額を日ごとカテゴリごとに集計

SELECT
  EXTRACT(DATE FROM t2.order_timestamp) AS `order_date`,
  t3.category,
  SUM(t3.total_price) AS total_price
FROM
  `next_drug.store` AS t1
INNER JOIN
  `next_drug.order` AS t2
ON
  t1.store_id = t2.store_id
INNER JOIN
  `next_drug.order_items` AS t3
ON
  t2.order_id = t3.order_id
WHERE
  t1.store = '横浜店'
GROUP BY
  1,
  2;
```

<walkthrough-info-message>**注:** Gemini は、同じプロンプトに対して異なる SQL クエリを提案する場合があります。必要に応じてクエリを修正してください。</walkthrough-info-message>

5. [**実行**] をクリックし、[**クエリ結果**] が表示されることを確認します。
クエリ結果は 124 件になるはずです (4 カテゴリ x 31 日間)。

## Data Canvas におけるテーブルの結合 (続き)

1. [**これらの結果に対してクエリを実行**] をクリックし、以下をプロンプトとして入力して実行します。
```
売上金額を日単位で合計して、時系列順に並び替える
```

Gemini は、次のような SQL クエリを生成します。
```terminal
# prompt: 売上金額を日単位で合計して、時系列順に並び替える

SELECT
  t1.order_date,
  SUM(t1.total_price) AS sum
FROM
  `SQL 1` AS t1
GROUP BY
  1
ORDER BY
  t1.order_date;
```

<walkthrough-info-message>**注:** Gemini は、同じプロンプトに対して異なる SQL クエリを提案する場合があります。必要に応じてクエリを修正してください。</walkthrough-info-message>

2. [**実行**] をクリックし、[**クエリ結果**] が表示されることを確認します。

3. [**可視化**] をクリックし、[**折れ線グラフの作成**] を選択します。

横浜店の売上推移を示す折れ線グラフが作成できました。

### **チャレンジ問題**
自由にデータキャンバスを操作して、その他のデータも可視化してみましょう。

* 横浜店のカテゴリごとの売上金額を示す円グラフを作成
* `store` テーブルと `order` テーブルから曜日ごとの各店舗の来店者数のヒートマップを作成

## **[シナリオ5] Looker Studio を用いてダッシュボードを作成する**

<walkthrough-tutorial-duration duration=15></walkthrough-tutorial-duration>

最後に、店舗マネージャーや経営陣がいつでもどこでも最新の分析結果を確認できるように、Looker Studio を使ってダッシュボードを共有します。ダッシュボードには、店舗別のKPI、顧客満足度の推移などが表示され、データに基づいた意思決定を支援します。

1. Data Canvas に表示されている、横浜店の売上金額の推移を表す折れ線グラフにマウスカーソルを合わせます。

2. グラフ右上の三点リーダーをクリックして [**Looker Studio にエクスポート**] をクリックします。

Looker Studio が開いて新しいダッシュボードが作成されます。

3. 追加されたグラフをドラッグして任意の位置に移動し、サイズを調整します。

## Looker Studio に BigQuery のデータを追加

次に、Looker Studio に可視化したい BigQuery のデータを追加します。

1. Looker Studio のメニューバーから [**Add data (データを追加)**] をクリックします。
ユーザーアカウントのセットアップを求められた場合は、画面の指示通りにします。

2. [**Connect to data (データに接続)**] セクションで [**BigQuery**] をクリックします。
アクセス権を求められた場合は承認してください。

3. マイプロジェクトからデータソースを次のとおり選択します。

フィールド | 値
---------------- | ----------------
プロジェクト | プロジェクトID
データセット | `next_drug`
表 | `customer_voice_analyzed`

4. [**Add (追加)**] をクリックします。続いて [**Add to report (レポートに追加)**] をクリックします。

## Looker Studioにグラフを追加

続いて、追加したデータを元に Looker Studio にグラフを追加します。

1. メニューバーの[**Add a chart (グラフを追加)**] > [**Pivot table (ピボットテーブル)**] > [**Pivot table with heatmap (ヒートマップ付きピボットテーブル)**] をクリックします。
2. 追加されたグラフを選択した状態で、[**Chart (グラフ)**] ペインでデータの設定をします。

フィールド | 値
---------------- | ----------------
Data source | `customer_voice_analyzed`
Row dimension (行) | `topic`
Column dimension (列) | `sentiment`
Metric (指標) | (AUT)`Record Count`

3. 追加されたグラフをドラッグして任意の位置に移動し、サイズを調整します。

これで Looker Studio のダッシュボードを用いて BigQuery のデータの可視化ができるようになりました。

### **チャレンジ問題**
Looker Studio にその他のテーブルやグラフも自由に追加して試してみてください。
* `top10_items` テーブルをデータソースとした棒グラフを表示する
* `daily_customer` テーブルをデータソースとした Google マップ (バブルマップ) を表示する

## Congratulations!
<walkthrough-conclusion-trophy></walkthrough-conclusion-trophy>

おめでとうございます！ハンズオンはこれで完了です。ご参加ありがとうございました。