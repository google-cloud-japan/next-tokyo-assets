'use strict'

const { BigQuery } = require('@google-cloud/bigquery')
const config = require('./config')

const bq = new BigQuery()

async function getProduct(index) {
    const query = `SELECT id, image 
    FROM \`${config.tableId}\` 
    LIMIT 1 OFFSET ${index}`
    const data = await bq.query(query)
    return data[0][0]
}

async function insertProduct(productId, image, product) {
    const insert = `INSERT \`${config.tableId}\`
    (id, image, title, categories, description, tags)
    VALUES (
        "${productId}", 
        "${image}",
        ${JSON.stringify(product.title)}, 
        ${JSON.stringify(product.categories)}, 
        ${JSON.stringify(product.description)}, 
        ${JSON.stringify(product.tags)}
    )`
    await bq.query(insert)
}

async function updateProduct(productId, image, product) {
    const insert = `UPDATE \`${config.tableId}\`
    SET title = ${JSON.stringify(product.title)}, 
    categories = ${JSON.stringify(product.categories)}, 
    description = ${JSON.stringify(product.description)}, 
    tags = ${JSON.stringify(product.tags)},
    image = ${image}
    WHERE id = "${productId}"`
    await bq.query(insert)
}

module.exports = { getProduct, insertProduct, updateProduct }