const project = process.env.PROJECT_ID
const region = process.env.REGION
const tableId = process.env.TABLE_ID
const bucket = process.env.BUCKET
const items = process.env.ITEMS
const taskIndex = process.env.CLOUD_RUN_TASK_INDEX ?? 0

module.exports = {
    project, region, tableId, bucket, items, taskIndex
}