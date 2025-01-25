import logging
from typing import Dict, List

import vertexai
from vertexai.generative_models import Content, GenerativeModel, Part, Tool, grounding

from Config.LlmConfig import GENERATIVE_MODEL_NAME, PROJECT_ID, SYSTEM_INSTRUCTION, VERTEX_AI_LOCATION
from Interfaces.ILlmGateway import ILlmGateway

logger = logging.getLogger(__name__)


class VertexAiGateway(ILlmGateway):
    """Vertex AIを使用したLLMゲートウェイの実装"""

    def __init__(self):
        """VertexAiGatewayの初期化"""
        # Vertex AI初期化
        vertexai.init(project=PROJECT_ID, location=VERTEX_AI_LOCATION)

        # グラウディングを使用するためのツールを定義
        self.tool = Tool.from_google_search_retrieval(grounding.GoogleSearchRetrieval())
        # 生成モデルの初期化
        self.model = GenerativeModel(
            model_name=GENERATIVE_MODEL_NAME,
            system_instruction=SYSTEM_INSTRUCTION,
            tools=[self.tool]
        )
        logger.info("Initialized VertexAiGateway")

    def generate_content(self, prompt: str, context: List[Dict[str, str]]) -> str:
        """
        プロンプトとコンテキストからVertex AIを使用して応答を生成する

        Args:
            prompt: ユーザーからの入力テキスト
            context: 会話の文脈情報

        Returns:
            生成された応答テキスト
        """
        contents = []
        # コンテキストを追加
        for message in context:
            contents.append(Content(
                role=message["role"],
                parts=[Part.from_text(message["content"])]
            ))

        # プロンプトを追加
        contents.append(Content(
            role="user",
            parts=[Part.from_text(prompt)]
        ))

        logger.debug(f"Generated contents structure: {contents}")

        try:
            logger.info("Calling Vertex AI GenerativeModel...")
            response = self.model.generate_content(contents=contents)
            logger.info("Successfully generated response")
            return response.text

        except Exception as err:
            logger.error(f"Error generating response: {err}", exc_info=True)
            raise 