from google.adk.agents import LlmAgent
from google.adk.tools.load_web_page import load_web_page

MODEL_GEMINI_2_5_PRO="gemini-2.5-PRO"
MODEL_GEMINI_2_5_FLASH="gemini-2.5-flash"
MODEL_GEMINI_2_5_FLASH_LITE="gemini-2.5-flash-lite"

agent = LlmAgent(
    name="learning_assistant",
    model=MODEL_GEMINI_2_5_FLASH,
    description="""ユーザーの学習を助けるために、できる限り正確な回答を返答するエージェントです。""",
    instruction="""あなたはユーザーの学習を助ける優秀なアシスタントです。ユーザーの質問にできる限り正確に回答してください。
1. あなたは URL を与えられたら、`load_web_page` ツールを利用し、コンテンツを取得します。
   URL を含まない質問の場合は、質問にできる限り正確に回答します。
2. URL のコンテンツを取得した場合は、コンテンツの内容を元に回答を生成します。""",
    tools=[load_web_page]
)

root_agent = agent
