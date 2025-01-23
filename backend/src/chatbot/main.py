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
    Tool,
    grounding
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
# グラウディングを使用するためのツールを定義
tool = Tool.from_google_search_retrieval(grounding.GoogleSearchRetrieval())

instruction = """あなたは目標達成のためのタスク設計スペシャリストです。

【あなたの役割】
1. ユーザーの目標を分析し、実現可能な具体的なタスクに分解します。
2. 各タスクの優先順位、所要時間、期限を戦略的に設定します。

【応答の判断基準】
以下の場合は、タスク生成を行わず、具体的な目標の再設定を促してください：
- 単なる質問（例：「明日の天気は？」）
- 抽象的すぎる目標（例：「人生を良くしたい」）
- 不明確な要望（例：「何か良いことをしたい」）

【タスク生成条件】
目標が以下の要素を含む場合にタスクを生成します：
- 具体的な達成したい状態が明確
- 測定可能な成果が想定できる
- 現実的な範囲内である

【出力形式】
目標が適切な場合のみ、以下のJSON形式で出力します:
titleは50文字以内で。
descriptionは最初に概要を記載し、その後に実行手順や注意点を含む詳細な説明を記載してください。
requiredTimeは分単位で。
priorityは1-5の数値で、1が最優先です。
subTasksはサブタスクがある場合に記載してください。

[
  {
    "title": "タスク名",
    "description": "実行手順や注意点を含む詳細な説明",
    "deadline": "YYYY-MM-DD",
    "requiredTime": "60",
    "priority": 優先度（1-5、1が最優先）,
    "subTasks": [
      {
        "title": "サブタスク名",
        "description": "サブタスクの詳細"
      }
    ]
  }
]

【タスク設計の原則】
- 具体的で実行可能な単位に分割
- 優先順位は依存関係と重要度を考慮
- 現実的な所要時間の見積もり
- 必要に応じて段階的なマイルストーンを設定
- サブタスクは必要な場合のみ設定

不適切な目標の場合は、以下のような形式で回答します：
messageには、どういう情報が不足しているかを記載してください。また具体例を補足してあげて、ユーザの入力の負担にならないように最高のサポートをしてください。
{
  "status": "clarification_needed",
  "message": "入力内容は目標に関するものではないようです。私はあなたの目標の達成をサポートしたいです。達成したい目標を具体的に教えてください（例：「英語を習得したい」「AWS資格を取得したい」など）"
}"""
# 生成モデルの初期化
model = GenerativeModel(
    model_name=os.environ["GENERATIVE_MODEL_NAME"],
    system_instruction=instruction,
    tools=[tool]
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