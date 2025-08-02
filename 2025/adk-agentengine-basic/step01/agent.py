from google.adk.agents import LlmAgent

MODEL_GEMINI_2_5_PRO="gemini-2.5-PRO"
MODEL_GEMINI_2_5_FLASH="gemini-2.5-flash"
MODEL_GEMINI_2_5_FLASH_LITE="gemini-2.5-flash-lite"

agent = LlmAgent(
    name="learning_assistant",
    model=MODEL_GEMINI_2_5_FLASH,
    description="""ユーザーの学習を助けるために、できる限り正確な回答を返答するエージェントです。""",
    instruction="""あなたはユーザーの学習を助ける優秀なアシスタントです。ユーザーの質問にできる限り正確に回答してください。""",
)

root_agent = agent
