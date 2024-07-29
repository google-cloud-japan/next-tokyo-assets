'use strict'
const { generate } = require('./gemini')
const { insertProduct } = require('./bq')
const config = require('./config')

const prompt = `
あなたはECサイトのコンテンツ管理者です。
添付した商品画像を元に、ECサイトに掲載する商品情報を作成してください。
レスポンスには次の属性を含めてください。

- title : 商品紹介ページのタイトルに表示する、魅力的な商品名。文字列。
- categories : 商品のカテゴリ。文字列の配列。
- description : 商品を紹介する説明文。文字列。
- tags : 商品のハッシュタグ。文字列の配列。
`

const main = async () => {
  const items = JSON.parse(config.items)
  const product = items[config.taskIndex]
  const productId = product.name.split('.')[0]
  const uri = `gs://${config.bucket}/${product.name}`
  console.info(`uri = ${uri}`)
  const response = await generate(uri, prompt)
  const parsedResponse = JSON.parse(response)
  await insertProduct(productId, product.name, parsedResponse)
  console.info(`success product id = ${productId}`)
}

main().catch(err => {
    console.error(err)
    process.exit(1)
})