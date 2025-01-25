import logging

from fastapi import APIRouter, HTTPException

from Http.Api.Schemas import ObjectiveGenerateRequest, ObjectiveGenerateResponse
from Infrastructure.Gateways.VertexAiGateway import VertexAiGateway
from Repositories.ChatRepository import ChatRepository
from Services.ChatService import ChatService
from UseCases.ObjectiveUseCase import ObjectiveUseCase
from UseCases.ObjectiveUseCaseInput import ObjectiveUseCaseInput

logger = logging.getLogger(__name__)

router = APIRouter()

# 依存関係の初期化
llm_gateway = VertexAiGateway()
chat_repository = ChatRepository()
chat_service = ChatService(llm_gateway)
objectiveUseCase = ObjectiveUseCase(chat_service, chat_repository)


@router.post("/api/objective/generate", response_model=ObjectiveGenerateResponse)
async def generate_objective(request: ObjectiveGenerateRequest) -> ObjectiveGenerateResponse:
    """
    ユーザが目標を設定したときに、その目標を達成するためのアクションを生成する

    Args:
        request (ObjectiveGenerateRequest): 目標生成リクエスト
            - prompt (str): ユーザからのプロンプト
            - objective_id (str): 目標のID

    Returns:
        ObjectiveGenerateResponse: 目標生成レスポンス
    """
    logger.info(f"Generating objective with prompt: {request.prompt} and objective_id: {request.objective_id}")
    result = objectiveUseCase.generate(ObjectiveUseCaseInput(request.prompt, request.objective_id))

    if result["status"] == "error":
        logger.error(f"Objective generation failed: {result['error']}")
        raise HTTPException(status_code=500, detail=result["error"])

    logger.info("Successfully generated objective actions")
    return result


@router.get("/api/health")
async def health_check() -> dict:
    """ヘルスチェックエンドポイント"""
    logger.debug("Health check requested")
    return {"status": "healthy"}
