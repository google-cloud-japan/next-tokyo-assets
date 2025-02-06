import logging

from fastapi import APIRouter, HTTPException, Request, Header
from cloudevents.http import from_http
from typing import Optional
from Http.Api.Schemas import (
    GoalGenerateRequest,
    GoalGenerateResponse,
    TaskSaveRequest,
    TaskSaveResponse,
)
from Infrastructure.Firebase.FirebaseClient import FirebaseClient
from Infrastructure.Gateways.VertexAiGateway import VertexAiGateway
from Repositories.ChatRepository import ChatHistoryRepository
from Repositories.TaskRepository import TaskRepository
from Services.ChatService import ChatService
from UseCases.GenerateTaskUseCase import GenerateTaskUseCase
from UseCases.SaveTaskUseCase import SaveTaskUseCase

from typing import List
from Services.TaskSyncService.task_sync_service import TaskSyncService


logger = logging.getLogger(__name__)

router = APIRouter()

# 依存関係の初期化
llmGateway = VertexAiGateway()
chatRepository = ChatHistoryRepository()
chatService = ChatService(llmGateway)
firebase_client = FirebaseClient.get_instance()
db = firebase_client.db
taskRepository = TaskRepository()


@router.post("/api/goal/generate", response_model=GoalGenerateResponse)
async def generate_goal(request: GoalGenerateRequest) -> GoalGenerateResponse:
    """
    通常のREST用エンドポイント。
    JSON形式で受け取ったrequest (GoalGenerateRequest) を使い、目標を生成する。
    """
    logger.info("Received REST request for goal generation (POST /api/goal/generate)")
    return _handle_goal_generation(
        prompt=request.prompt,
        userId=request.userId,
        goalId=request.goalId,
        deadline=request.deadline,
        weeklyHours=request.weeklyHours,
    )


@router.post("/api/goal/generate/eventarc")
async def generate_goal_eventarc(request: Request) -> dict:
    """
    Firestore の書き込みなどで発生したイベント (Eventarc) を受け取るエンドポイント。
    CloudEvent形式のリクエストを解析し、Firestore からドキュメントを再取得して
    既存のビジネスロジック (_handle_goal_generation) を呼び出す。
    """

    logger.info("Received Eventarc request for goal generation")

    # 1. CloudEvents のパース
    raw_body = await request.body()
    try:
        event = from_http(request.headers, raw_body)
    except Exception as e:
        logger.error(f"Failed to parse CloudEvent: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=f"Invalid CloudEvent: {e}")

    # 2. 'document' などから Firestore のパスを取得する (例: "users/UID/goals/GOAL_ID")
    document_path = event.get("document")
    if not document_path:
        logger.error("No 'document' field found in CloudEvent")
        raise HTTPException(status_code=400, detail="No document path in CloudEvent")

    logger.info(f"CloudEvent document path: {document_path}")

    # 3. Firestore からドキュメントを読み込む
    #    例: "users/{uid}/goals/{goalId}" => collection("users").doc(uid).collection("goals").doc(goalId)
    parts = document_path.split("/")
    if len(parts) < 4:
        logger.error("Document path format is invalid")
        raise HTTPException(status_code=400, detail="Invalid Firestore document path")

    # 例: users/{uid}/goals/{goalId}
    # parts[0] = "users"
    # parts[1] = uid
    # parts[2] = "goals"
    # parts[3] = goalId
    uid = parts[1]
    goalId = parts[3]

    doc_ref = db.collection("users").document(uid).collection("goals").document(goalId)
    doc_snapshot = doc_ref.get()
    if not doc_snapshot.exists:
        logger.error("Target document not found in Firestore")
        raise HTTPException(status_code=404, detail="Document not found")

    doc_data = doc_snapshot.to_dict()
    # doc_data 内に "prompt", "deadline", "weeklyHours" などが保存されている想定
    logger.info(f"Fetched doc_data from Firestore: {doc_data}")

    prompt = doc_data.get("prompt", "")
    deadline = doc_data.get("deadline")
    weeklyHours = doc_data.get("weeklyHours")

    # userId は `uid` でもいいし、doc_data に格納している場合はそちらを参照
    # ここでは単純化して "userId" = uid として使う例
    userId = uid

    # 4. 既存の処理 (ユースケース) を呼び出す
    #    エラー処理などは _handle_goal_generation 内で行う。
    # 追加のログ：最終的にユースケースに渡す値を表示
    logger.info(
        f"Eventarc generation params -> prompt: {prompt}, userId: {userId}, "
        f"goalId: {goalId}, deadline: {deadline}, weeklyHours: {weeklyHours}"
    )
    try:
        result = _handle_goal_generation(
            prompt=prompt,
            userId=userId,
            goalId=goalId,
            deadline=deadline,
            weeklyHours=weeklyHours,
        )
    except HTTPException as http_ex:
        # エラーがあればそのまま再送
        logger.error("Error in goal generation from eventarc", exc_info=True)
        raise http_ex
    except Exception as e:
        logger.error("Unknown error in goal generation from eventarc", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

    logger.info("Successfully handled goal generation via Eventarc")
    # 必要に応じて Firestore に書き戻す等の処理を追加

    # 通常の REST エンドポイントでは GoalGenerateResponse を返すが、
    # Eventarc 用なので {"status":"ok","message":"..."} とかのシンプルなレスポンスでもOK
    return {"status": "success", "message": "Goal generated successfully via Eventarc"}


def _handle_goal_generation(
    prompt: str,
    userId: str,
    goalId: str = None,
    deadline: str = None,
    weeklyHours: float = None,
) -> GoalGenerateResponse:
    """
    既存のビジネスロジックをカプセル化。
    /api/goal/generate (REST) からも、/api/goal/generate/eventarc (Eventarc) からも
    この共通関数を呼び出す形にして重複を減らす。
    """

    useCase = GenerateTaskUseCase(chatService, chatRepository, taskRepository)
    goalUseCaseInput = useCase.Input(
        prompt=prompt,
        userId=userId,
        goalId=goalId,
        deadline=deadline,
        weeklyHours=weeklyHours,
    )
    goalUseCaseOutput = useCase.generate(goalUseCaseInput)

    if goalUseCaseOutput.status == "error":
        logger.error(f"Goal generation failed: {goalUseCaseOutput}")
        raise HTTPException(status_code=500, detail=goalUseCaseOutput.errorMessage)

    if goalUseCaseOutput.status == "please_retype_prompt":
        logger.error(f"Goal generation needs retyping: {goalUseCaseOutput}")
        return GoalGenerateResponse(
            status="please_retype_prompt",
            message=goalUseCaseOutput.message,
            tasks=[],
            error=goalUseCaseOutput.errorMessage,
        )

    return GoalGenerateResponse(
        status=goalUseCaseOutput.status,
        message=goalUseCaseOutput.message,
        tasks=goalUseCaseOutput.tasks,
        error=goalUseCaseOutput.errorMessage,
    )

@router.post("/sync-tasks")
def sync_tasks_endpoint(tasks: List[dict],   
                        authorization: Optional[str] = Header(None)
):
    """
    受け取ったタスクリストを TaskSyncService に渡して
    Google Tasks と連携処理を行うエンドポイント。
    """
    if not authorization or not authorization.startswith("Bearer "):
        return {"error": "No or invalid access token"}

    access_token = authorization.replace("Bearer ", "")

    service = TaskSyncService(
        access_token=access_token
    )
    # Pydanticモデルをdictに変換し、リスト化してsync_tasksに渡す
    # tasks_dict_list = [task.dict() for task in tasks]
    result = service.sync_tasks(tasks, access_token)
    return result

@router.post("/api/task/save", response_model=TaskSaveResponse)
async def save_task(request: TaskSaveRequest) -> TaskSaveResponse:
    """
    ユーザがタスクを保存したときに、そのタスクを保存する
    """
    saveTaskUseCase = SaveTaskUseCase(TaskRepository())

    # Pydanticモデルを辞書に変換
    task_dicts = [task.dict() for task in request.tasks]

    saveTaskUseCaseInput = saveTaskUseCase.Input(
        tasks=task_dicts,
        userId=request.userId,
        goalId=request.goalId,
    )

    saveTaskUseCaseOutput = saveTaskUseCase.save(saveTaskUseCaseInput)
    return TaskSaveResponse(
        success=saveTaskUseCaseOutput.success,
        message=saveTaskUseCaseOutput.message,
        error=saveTaskUseCaseOutput.errorMessage,
    )


@router.get("/api/health")
async def health_check() -> dict:
    """ヘルスチェックエンドポイント"""
    logger.debug("Health check requested")
    return {"status": "healthy"}
