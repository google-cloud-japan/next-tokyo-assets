from typing import Optional

from pydantic import BaseModel, Field


class ObjectiveGenerateRequest(BaseModel):
    """目標生成リクエストのスキーマ定義"""
    prompt: str = Field(..., description="ユーザーからの目標入力")
    objective_id: Optional[str] = Field(None, description="目標を識別するためのID")


class ObjectiveGenerateResponse(BaseModel):
    """目標生成レスポンスのスキーマ定義"""
    status: str = Field(..., description="処理の状態 (success/error)")
    response: str = Field(..., description="生成された応答テキスト")
    prompt: str = Field(..., description="入力されたプロンプト")
    objective_id: str = Field(..., description="目標ID")
    error: Optional[str] = Field(None, description="エラーが発生した場合のメッセージ") 