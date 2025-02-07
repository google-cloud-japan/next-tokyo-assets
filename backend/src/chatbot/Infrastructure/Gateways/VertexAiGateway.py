import json
import logging
import os
from datetime import datetime
from typing import List

import vertexai
from vertexai.generative_models import (
    Content,
    GenerationConfig,
    GenerativeModel,
    Part,
    Tool,
    grounding,
)


from Domain.Models.Chat import ChatMessage
from Domain.Models.Task import Task
from Domain.Models.TaskCollection import TaskCollection
from Infrastructure.Gateways.LlmConfigFactory import LlmConfig
from Interfaces.ILlmGateway import ILlmGateway, GenerationResult

logger = logging.getLogger(__name__)

# Vertex AI設定
PROJECT_ID = os.environ["PROJECT_ID"]
VERTEX_AI_LOCATION = os.environ["VERTEX_AI_LOCATION"]
GENERATIVE_MODEL_NAME = os.environ["GENERATIVE_MODEL_NAME"]


class VertexAiGateway(ILlmGateway):
    # 応答のステータス
    # ステータスは、successまたはclarification_neededのいずれかをプロンプトで定義しています。変更・追加をしたい場合はプロンプトを変更してください。
    # clarification_neededは目標でないと判断された場合に返すステータスです。
    RESPONSE_STATUS = {
        "success": "success",
        "clarification_needed": "clarification_needed",
    }
    """Vertex AIを使用したLLMゲートウェイの実装"""

    def __init__(self, config: LlmConfig):
        """VertexAiGatewayの初期化"""
        vertexai.init(project=PROJECT_ID, location=VERTEX_AI_LOCATION)
        self.tool = Tool.from_google_search_retrieval(grounding.GoogleSearchRetrieval())
        self.model = GenerativeModel(
            model_name=GENERATIVE_MODEL_NAME,
            system_instruction=config.system_instruction,
            tools=[self.tool],
            generation_config=GenerationConfig(
                response_mime_type=config.response_mime_type,
                response_schema=config.response_schema,
            ),
        )
        logger.info("Initialized VertexAiGateway")

    def generateTask(self, prompt: str, context: List[ChatMessage]) -> GenerationResult:
        """
        プロンプトとコンテキストからVertex AIを使用して応答を生成する

        Args:
            prompt: ユーザーからの入力テキスト
            context: 会話の文脈情報

        Returns:
            生成された応答テキスト
        """
        try:
            # ドメインモデルのデータをLLMが求めるデータに変換する
            contents = self._convertChatMessagesToContents(context, prompt)
            # LLMにデータを渡して応答を生成する
            logger.info("Calling Vertex AI GenerativeModel...")
            response = self.model.generate_content(contents=contents)
            # レスポンスをJSONにパース
            response_list = json.loads(response.text)
            if not isinstance(response_list, list) or len(response_list) == 0:
                return GenerationResult.error(errorMessage="Invalid response format")

            response_dict = response_list[0]
            # 目標でないと判断された場合
            if (
                response_dict.get("status")
                == self.RESPONSE_STATUS["clarification_needed"]
            ):
                return GenerationResult.error(
                    errorMessage="目標のプロンプトを入力してください",
                    llmResponse=response_dict.get("message"),
                )

            # タスクの生成
            taskCollection = self._convertJsonToTaskCollection(
                response_dict.get("tasks", [])
            )

            return GenerationResult.success(
                data={"tasks": taskCollection}, message=response_dict.get("message")
            )

        except json.JSONDecodeError:
            return GenerationResult.error(errorMessage="JSON解析エラー")
        except (KeyError, IndexError, TypeError) as err:
            logger.error(f"Error generating response: {err}", exc_info=True)
            return GenerationResult.error(
                errorMessage="応答の形式が不正です。もう一度お試しください。"
            )
        except ValueError as e:
            logger.error(f"Error generating response: {e}", exc_info=True)
            return GenerationResult.error(
                errorMessage=f"無効な値が含まれています。もう一度お試しください。: {e}"
            )
        except TimeoutError:
            logger.error("TimeoutError", exc_info=True)
            return GenerationResult.error(errorMessage="処理タイムアウト")
        except Exception as err:
            logger.error(f"Error generating response: {err}", exc_info=True)
            return GenerationResult.error(errorMessage="予期せぬエラーが発生しました。")

    def _convertChatMessagesToContents(
        self, messages: List[ChatMessage], prompt: str
    ) -> List[Content]:
        """
        ChatMessageのリストをLLMが求めるContent形式に変換する
        """
        contents = []

        # チャット履歴を変換
        for message in messages:
            contents.append(
                Content(
                    role=message.role,
                    parts=[Part.from_text(message.content)]
                )
            )

        # ユーザーの新しい入力を追加
        contents.append(
            Content(
                role="user",
                parts=[Part.from_text(prompt)]
            )
        )

        return contents

    def _convertJsonToTaskCollection(self, tasksJson: List[dict]) -> TaskCollection:
        taskCollection = TaskCollection()
        for task_dict in tasksJson:
            task = Task(
                title=task_dict["title"],
                description=task_dict["description"],
                deadline=datetime.strptime(task_dict["deadline"], "%Y-%m-%d").date(),
                requiredTime=int(task_dict["requiredTime"]),
                priority=int(task_dict["priority"]),
            )
            taskCollection.add(task)
        return taskCollection

    def generateMessage(self, prompt: str, context: List[ChatMessage]) -> GenerationResult:
        """
        プロンプトとコンテキストからVertex AIを使用してメッセージを生成する
        """
            # ドメインモデルのデータをLLMが求めるデータに変換する
        contents = self._convertChatMessagesToContents(context, prompt)
        # LLMにデータを渡して応答を生成する
        logger.info("Calling Vertex AI GenerativeModel...")
        response = self.model.generate_content(contents=contents)

        return GenerationResult.success(message=response.text)


