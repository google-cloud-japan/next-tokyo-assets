import json
import logging
from datetime import datetime
from typing import List

import vertexai
from vertexai.generative_models import Content, GenerationConfig, GenerativeModel, Part, Tool, grounding

from Config.LlmConfig import GENERATIVE_MODEL_NAME, PROJECT_ID, SYSTEM_INSTRUCTION, VERTEX_AI_LOCATION
from Domain.Models.Chat import ChatMessage
from Domain.Models.Task import Task
from Domain.Models.TaskCollection import TaskCollection
from Interfaces.ILlmGateway import RESPONSE_SCHEMA, ILlmGateway, TaskGenerationResult

logger = logging.getLogger(__name__)

class VertexAiGateway(ILlmGateway):
    # 応答のステータス
    # ステータスは、successまたはclarification_neededのいずれかをプロンプトで定義しています。変更・追加をしたい場合はプロンプトを変更してください。
    # clarification_neededは目標でないと判断された場合に返すステータスです。
    RESPONSE_STATUS = {
        "success": "success",
        "clarification_needed": "clarification_needed",
    }
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
            tools=[self.tool],
            generation_config=GenerationConfig(
                response_mime_type="application/json",
                response_schema=RESPONSE_SCHEMA,
            ),
        )
        logger.info("Initialized VertexAiGateway")

    def generateTask(self, prompt: str, context: List[ChatMessage]) -> TaskGenerationResult:
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
                return TaskGenerationResult.error(errorMessage="Invalid response format")

            response_dict = response_list[0]
            # 目標でないと判断された場合
            if response_dict.get("status") == self.RESPONSE_STATUS["clarification_needed"]:
                return TaskGenerationResult.error(
                    errorMessage="目標のプロンプトを入力してください",
                    llmResponse=response_dict.get("message")
                )

            # タスクの生成
            taskCollection = self._convertJsonToTaskCollection(response_dict.get("tasks",[]))

            return TaskGenerationResult.success(
                tasks=taskCollection,
                llmResponse=response_dict.get("message")
            )

        except json.JSONDecodeError:
            return TaskGenerationResult.error(errorMessage="JSON解析エラー")
        except (KeyError, IndexError, TypeError) as err:
            logger.error(f"Error generating response: {err}", exc_info=True)
            return TaskGenerationResult.error(errorMessage="応答の形式が不正です。もう一度お試しください。")
        except ValueError as e:
            logger.error(f"Error generating response: {e}", exc_info=True)
            return TaskGenerationResult.error(errorMessage=f"無効な値が含まれています。もう一度お試しください。: {e}")
        except TimeoutError:
            logger.error("TimeoutError", exc_info=True)
            return TaskGenerationResult.error(errorMessage="処理タイムアウト")
        except Exception as err:
            logger.error(f"Error generating response: {err}", exc_info=True)
            return TaskGenerationResult.error(errorMessage="予期せぬエラーが発生しました。")

    def _convertChatMessagesToContents(self, messages: List[ChatMessage], prompt: str) -> List[Content]:
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


