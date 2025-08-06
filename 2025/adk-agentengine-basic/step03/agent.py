from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import StdioConnectionParams
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from mcp import StdioServerParameters

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
    -   質問にURLが含まれているか確認してください。

2.  **情報収集 (URLがある場合)**:
    -   質問に1つまたは複数のURLが含まれている場合、各URLに対して `fetch` ツールを必ず使用して、ウェブページの内容を取得してください。その際、`max_length` パラメータに `100000` を指定してください。
    -   `fetch` ツールが失敗した場合や、URLから有益な情報を得られなかった場合は、その旨をユーザーに伝えた上で、自身の知識で回答を試みてください。

3.  **回答生成**:
    -   **URLから情報を取得した場合**: 取得したすべての内容を唯一の情報源として、ユーザーの質問に回答してください。取得した情報にないことは回答に含めず、事実に基づいた回答を心がけてください。
    -   **URLがない場合**: あなた自身の知識を用いて、ユーザーの質問にできる限り正確かつ詳細に回答してください。
    -   回答は、常に中立的で分かりやすい言葉で構成してください。
""",
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
