from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import StdioConnectionParams
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from mcp import StdioServerParameters

MODEL_GEMINI_2_5_PRO="gemini-2.5-PRO"
MODEL_GEMINI_2_5_FLASH="gemini-2.5-flash"
MODEL_GEMINI_2_5_FLASH_LITE="gemini-2.5-flash-lite"

agent = LlmAgent(
    name="learning_assistant",
    model=MODEL_GEMINI_2_5_FLASH,
    description="""ユーザーの学習を助けるために、できる限り正確な回答を返答するエージェントです。""",
    instruction="""あなたはユーザーの学習を助ける優秀なアシスタントです。ユーザーの質問にできる限り正確に回答してください。
1. あなたは URL を与えられたら、`fetch` ツールを利用し、コンテンツを取得します。
   また複数の URL を受け取った場合は `fetch` をそれぞれの URL について呼び出します。
   URL を含まない質問の場合は、質問にできる限り正確に回答します。
2. 単一の URL、または複数の URL からコンテンツを取得した場合は、コンテンツの内容すべてを元に回答を生成します。""",
    tools=[
        MCPToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command='uvx',
                    args=[
                        "mcp-server-fetch",
                    ],
                ),
                timeout=20,
            ),
        ),
    ]
)

root_agent = agent
