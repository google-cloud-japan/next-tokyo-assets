import logging
from typing import Dict

from Interfaces.ILlmGateway import ILlmGateway

logger = logging.getLogger(__name__)


class ChatService:
    """チャットボットのコアロジックを担当するクラス"""

    def __init__(self, llm_gateway: ILlmGateway):
        """
        ChatServiceの初期化

        Args:
            llm_gateway: LLMゲートウェイ
        """
        self.llm_gateway = llm_gateway
        logger.info("Initialized ChatService")

    def generate_response(self, prompt: str, chat_history: list = None) -> Dict[str, str]:
        """
        プロンプトとチャット履歴から応答を生成する

        Args:
            prompt: ユーザーからの入力テキスト
            chat_history: チャット履歴

        Returns:
            生成された応答を含む辞書
        """
        try:
            # LLMを使用して応答を生成
            response_text = self.llm_gateway.generate_content(prompt, chat_history or [])
            logger.info("Generated response from LLM")

            # レスポンスの作成
            return {"status": "success", "response": response_text, "prompt": prompt}

        except Exception as err:
            logger.error(f"Error in generate_response: {err}", exc_info=True)
            return {
                "status": "error",
                "response": "申し訳ございません。応答の生成に失敗しました。",
                "error": str(err),
                "prompt": prompt,
            }
