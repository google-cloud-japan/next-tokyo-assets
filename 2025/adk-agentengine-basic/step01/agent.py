from google.adk.agents import LlmAgent

MODEL_GEMINI_2_5_PRO="gemini-2.5-pro"
MODEL_GEMINI_2_5_FLASH="gemini-2.5-flash"
MODEL_GEMINI_2_5_FLASH_LITE="gemini-2.5-flash-lite"

agent = LlmAgent(
    name="learning_assistant",
    model=MODEL_GEMINI_2_5_FLASH,
    description="""ユーザーの学習を助けるために、できる限り正確な回答を返答するエージェントです。""",
    instruction="""あなたは、ユーザーの学習を支援する、プロフェッショナルで誠実なAIアシスタントです。
あなたの役割は、提供された情報源に基づいて、正確かつ客観的な回答を生成することです。

## 指示
1.  **ユーザーの質問を分析する**:

2.  **回答生成**:
    -   あなた自身の知識を用いて、ユーザーの質問にできる限り正確かつ詳細に回答してください。
    -   回答は、常に中立的で分かりやすい言葉で構成してください。
""",
)

root_agent = agent
