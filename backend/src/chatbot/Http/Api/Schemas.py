from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field

class GoalGenerateRequest(BaseModel):
    """目標生成リクエストのスキーマ定義"""

    prompt: str = Field(..., description="ユーザーが入力した目標")
    userId: str = Field(..., description="ユーザーID Firebase Auth ID")
    goalId: Optional[str] = Field(None, description="ユーザが設定した目標ID")
    deadline: Optional[str] = Field(None, description="目標の期日 (YYYY-MM-DD形式) 目標をいつまでに達成したいか")
    weeklyHours: Optional[int] = Field(None, description="週あたりの作業時間 (時間) 目標を達成するために1週間にかける時間")

class Task(BaseModel):
    """タスクのスキーマ定義"""

    title: str = Field(..., description="タスクのタイトル", max_length=50)
    description: str = Field(..., description="タスクの説明")
    deadline: date = Field(..., description="タスクの期限")
    requiredTime: int = Field(..., description="タスクの所要時間（分）", gt=0)
    priority: int = Field(..., description="タスクの優先度（1-5、1が最優先）", ge=1, le=5)

class GoalGenerateResponse(BaseModel):
    """目標生成レスポンスのスキーマ定義"""

    status: str = Field(..., description="処理の状態 (success/error)")
    message: str = Field(..., description="LLMからのメッセージ 画面に表示するメッセージ")
    tasks: List[Task] = Field(..., description="生成されたタスクリスト")
    error: Optional[str] = Field(None, description="エラーが発生した場合のメッセージ")
