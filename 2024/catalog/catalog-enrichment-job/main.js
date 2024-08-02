'use strict'
const { generate } = require('./gemini')
const { insertProduct } = require('./bq')
const config = require('./config')

const prompt = `
あなたはECサイトのコンテンツ管理者です。
添付した商品画像を元に、ECサイトに掲載する商品情報を作成してください。
レスポンスには次の属性を含めてください。
JSON 形式で出力してください。

- title : 商品紹介ページのタイトルに表示する、魅力的な商品名。String。
- description : 商品を紹介する説明文。String。
- categories : 商品のカテゴリ。文字列の配列。
- tags : 商品のハッシュタグ。文字列の配列。
`

const express = require("express")
const app = express()

app.use(express.json())
app.use(express.urlencoded({
  extended: true
}))

const server = app.listen(3000, function(){
  console.log("Node.js is listening to PORT:" + server.address().port)
})

app.post("/gen", function(req, res, next){
  console.log(req.body.product)
  const product = req.body.product
  main(product).then(() => {
    res.json({ message: 'OK' })
  }).catch(e => {
    throw e
  })
})

const main = async (product) => {
  const productId = product.name.split('.')[0]
  const uri = `gs://${config.bucket}/${product.name}`
  console.info(`uri = ${uri}`)
  const response = await generate(uri, prompt)
  const parsedResponse = JSON.parse(response)
  await insertProduct(productId, product.name, parsedResponse)
  console.info(`success product id = ${productId}`)
}