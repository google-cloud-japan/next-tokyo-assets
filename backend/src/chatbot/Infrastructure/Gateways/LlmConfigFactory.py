from pydantic import BaseModel

from Config.Llm import GenerateTasksConfig, GenerateChatConfig


class LlmConfig(BaseModel):
    response_mime_type: str
    response_schema: dict | None = None
    system_instruction: str| None

class LlmConfigFactory:
    """
    LLMの設定を生成するファクトリークラス
    タスク生成やQAなど、ユースケースごとに異なるLLM設定を提供する
    """
    @classmethod
    def create_task_config(cls):

        return LlmConfig(
            response_mime_type=GenerateTasksConfig.RESPONSE_MIME_TYPE,
            response_schema=GenerateTasksConfig.RESPONSE_SCHEMA,
            system_instruction=GenerateTasksConfig.SYSTEM_INSTRUCTION,
        )

    @classmethod
    def create_qa_config(cls):
        return LlmConfig(
            response_mime_type=GenerateChatConfig.RESPONSE_MIME_TYPE,
            system_instruction=GenerateChatConfig.SYSTEM_INSTRUCTION
        )