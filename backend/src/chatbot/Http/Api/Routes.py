import json
import logging

from fastapi import APIRouter, HTTPException

from Http.Api.Schemas import GoalGenerateRequest, GoalGenerateResponse
from Infrastructure.Gateways.VertexAiGateway import VertexAiGateway
from Repositories.ChatRepository import ChatHistoryRepository
from Services.ChatService import ChatService
from UseCases.GenerateTaskUseCase import GenerateTaskUseCase
from pydantic import BaseModel
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


logger = logging.getLogger(__name__)

router = APIRouter()

# 依存関係の初期化
llmGateway = VertexAiGateway()
chatRepository = ChatHistoryRepository()
chatService = ChatService(llmGateway)

class TokenData(BaseModel):
    access_token: str

@router.post("/api/goal/generate", response_model=GoalGenerateResponse)
async def generate_goal(request: GoalGenerateRequest) -> GoalGenerateResponse:
    """
    ユーザが目標を設定したときに、その目標を達成するためのアクションを生成する

    Args:
        request (GoalGenerateRequest): 目標生成リクエスト
            - prompt (str): ユーザからのプロンプト
            - objective_id (str): 目標のID

    Returns:
        ObjectiveGenerateResponse: 目標生成レスポンス
    """

    # ユーザが目標を設定したときに、その目標を達成するためのアクションを生成する
    useCase = GenerateTaskUseCase(chatService, chatRepository)
    # プレゼンテーション層から受け取ったデータをユースケース層が求めているデータに変換する
    goalUseCaseInput = useCase.Input(
        prompt=request.prompt,
        userId=request.userId,
        goalId=request.goalId or None,
        deadline=request.deadline or None,
        weeklyHours=request.weeklyHours or None,
    )
    goalUseCaseOutput = useCase.generate(goalUseCaseInput)

    if goalUseCaseOutput.status == "error":
        logger.error(f"Goal generation failed: {goalUseCaseOutput}")
        raise HTTPException(status_code=500, detail=goalUseCaseOutput.errorMessage)

    if goalUseCaseOutput.status == "please_retype_prompt":
        logger.error(f"Goal generation failed: {goalUseCaseOutput}")
        return GoalGenerateResponse(
            status="please_retype_prompt",
            message=goalUseCaseOutput.message,
            tasks=[],
            error=goalUseCaseOutput.errorMessage,
        )

    # アプリケーション層の値をプレゼンテーション層のデータに変換して返す

    response = GoalGenerateResponse(
        status=goalUseCaseOutput.status,
        message=goalUseCaseOutput.message,
        tasks=goalUseCaseOutput.tasks,
        error=goalUseCaseOutput.errorMessage,
    )

    return response


@router.post("/addEvent")
def add_event(token_data: TokenData):
    """
        Google認証のテスト用API
    """
    # 1) GoogleカレンダーAPIのクライアントを初期化
    creds = Credentials(token=token_data.access_token)
    service = build("calendar", "v3", credentials=creds)

    # 2) 追加するイベントの情報
    event = {
        'summary': 'テストイベント',
        'location': 'Tokyo',
        'description': 'これはテスト',
        'start': {
            'dateTime': '2025-02-01T09:00:00',
            'timeZone': 'Asia/Tokyo',
        },
        'end': {
            'dateTime': '2025-02-01T10:00:00',
            'timeZone': 'Asia/Tokyo',
        },
    }

    # 3) イベントをインサート
    created_event = service.events().insert(calendarId='primary', body=event).execute()

    return {"status": "ok", "created_event": created_event}


@router.get("/api/health")
async def health_check() -> dict:
    """ヘルスチェックエンドポイント"""
    logger.debug("Health check requested")
    return {"status": "healthy"}
