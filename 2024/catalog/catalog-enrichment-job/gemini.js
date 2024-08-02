'use strict'

const { VertexAI } = require('@google-cloud/vertexai')
const config = require('./config')

const vertexAI = new VertexAI({ project: config.project, location: config.region })
const model = vertexAI.preview.getGenerativeModel({
    model: 'gemini-1.5-flash',
    generationConfig: {
        maxOutputTokens: 2048,
        temperature: 0.4,
        topP: 1,
        topK: 32,
        responseMimeType: 'application/json'
    }
})

async function generate(uri, prompt) {
    const textPart = {
        text: prompt
      }
      const filePart = {
        fileData: {
          fileUri: uri,
          mimeType: 'image/png',
        }
      }
      const request = {
        contents: [{
            role: 'user',
            parts: [
              textPart,
              filePart
            ]
          }
        ]
      }
      const content = await model.generateContent(request)
    const response = await content.response
    const text = response.candidates[0].content.parts[0].text
    return text
}

module.exports = { generate }