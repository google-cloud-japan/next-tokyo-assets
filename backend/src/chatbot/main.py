"""FastAPI based chatbot application using Vertex AI."""

import logging
import os
from typing import List, Dict, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import vertexai
from vertexai.generative_models import (
    Content,
    Part,
    GenerativeModel,
)

from firestore.store import save_chat_response

# ロガーの設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ChatRequest(BaseModel):
    """チャットリクエストのスキーマ定義"""
    prompt: str
    chat_history: List[Dict[str, str]] = []


class ChatResponse(BaseModel):
    """チャットレスポンスのスキーマ定義"""
    status: str
    response: str
    prompt: str
    error: Optional[str] = None


# FastAPIアプリケーションの初期化
app = FastAPI(title="Chatbot API", description="Vertex AIを使用したチャットボットAPI")

# Vertex AI初期化
vertexai.init(project=os.environ["PROJECT_ID"], location=os.environ["VERTEX_AI_LOCATION"])

# 生成モデルの初期化
model = GenerativeModel(
    model_name=os.environ["GENERATIVE_MODEL_NAME"],
    system_instruction=["あなたは親切で丁寧な日本語アシスタントです。"],
)


def generate_response(prompt: str, chat_history: List[Dict[str, str]] = None) -> Dict[str, str]:
    """
    プロンプトとチャット履歴から応答を生成する

    Args:
        prompt: ユーザーからの入力テキスト
        chat_history: 過去のチャット履歴

    Returns:
        生成された応答を含む辞書
    """
    if chat_history is None:
        chat_history = []

    logger.info(f"Generating response for prompt: {prompt[:100]}...")
    logger.info(f"Chat history length: {len(chat_history)}")

    contents = []
    for message in chat_history:
        contents.append(Content(
            role=message["role"],
            parts=[Part.from_text(message["content"])]
        ))

    contents.append(Content(
        role="user",
        parts=[Part.from_text(prompt)]
    ))

    logger.debug(f"Generated contents structure: {contents}")

    try:
        logger.info("Calling Vertex AI GenerativeModel...")
        response = model.generate_content(contents=contents)
        logger.info("Successfully generated response")

        result = {
            "status": "success",
            "response": response.text,
            "prompt": prompt
        }

        # Firestore に応答を保存
        save_chat_response(result)

        return result

    except Exception as err:
        logger.error(f"Error generating response: {err}", exc_info=True)
        return {
            "status": "error",
            "response": "申し訳ございません。応答の生成に失敗しました。",
            "error": str(err),
            "prompt": prompt
        }


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest) -> ChatResponse:
    """
    チャットエンドポイント

    Args:
        request: チャットリクエスト

    Returns:
        生成された応答
    """
    logger.info("Received chat request")
    result = generate_response(request.prompt, request.chat_history)

    if result["status"] == "error":
        logger.error(f"Chat request failed: {result['error']}")
        raise HTTPException(status_code=500, detail=result["error"])

    logger.info("Successfully processed chat request")
    return result


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """ヘルスチェックエンドポイント"""
    logger.debug("Health check requested")
    return {"status": "healthy"}


# アプリケーション起動時のログ
logger.info(
    f"Application started with project ID: {os.environ['PROJECT_ID']} "
    f"in location: {os.environ['VERTEX_AI_LOCATION']}"
)