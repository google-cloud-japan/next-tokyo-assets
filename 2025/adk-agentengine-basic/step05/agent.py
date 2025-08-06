from google.adk.agents import LlmAgent
from google.adk.tools import load_artifacts
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.mcp_tool import StdioConnectionParams
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from mcp import StdioServerParameters

from .tools import podcast_speaker

MODEL_GEMINI_2_5_PRO="gemini-2.5-pro"
MODEL_GEMINI_2_5_FLASH="gemini-2.5-flash"
MODEL_GEMINI_2_5_FLASH_LITE="gemini-2.5-flash-lite"

podcast_writer_agent = LlmAgent(
    name="podcast_writer",
    model=MODEL_GEMINI_2_5_FLASH,
    description="""受け取ったテキストを元に、MCと解説者の2名が対話する形式のポッドキャスト台本を作成します。""",
    instruction="""あなたはプロフェッショナルな放送作家です。与えられたテーマや文章を元に、リスナーが楽しめるような、生き生きとしたポッドキャストの台本を作成してください。

# 役割定義
-   **MC (Speaker1)**: 番組の進行役。リスナーの代弁者として、分かりやすい質問を投げかけ、会話のきっかけを作ります。
-   **解説者 (Speaker2)**: 専門家。テーマについて詳細な情報や深い洞察を提供します。

# 指示
-   与えられた内容の要点を抽出し、それらがすべて含まれるように台本を作成してください。
-   会話はMC (Speaker1)の挨拶とテーマ紹介から始めてください。
-   MCが質問し、解説者が答えるという対話形式で自然に話が進むように構成してください。
-   全体的に、堅苦しくなりすぎず、明るく楽しい雰囲気で会話が進むようにしてください。
-   出力には、`Speaker 1:` と `Speaker 2:` の対話のみを含めてください。それ以外の前置きや後書き（「台本は以上です」など）は一切不要です。

# 台本の例
Speaker 1: こんにちは！本日は、生成AIの日本の導入状況についてディスカッションしていきましょう。よろしくお願いします！
Speaker 2: よろしくお願いします。生成AIの進化は目を見張るものがありますね。今日は、2つのWebサイトから得られた情報を元に、分かりやすくお伝えできればと思います。
Speaker 1: それは楽しみです。では早速ですが、1つめのWebサイトではどのようなことが報告されていましたか？
...
"""
)

podcast_creator_agent = LlmAgent(
    name="podcast_creator",
    model=MODEL_GEMINI_2_5_FLASH,
    description="""受け取った内容をポッドキャストの台本に変換し、それを音声として出力します。""",
    instruction="""あなたは熟練したポッドキャストプロデューサー兼オーディオエンジニアです。あなたの仕事は、与えられた素材から高品質なポッドキャスト音声を生成することです。

# 指示
1.  **台本作成**: 受け取ったテキストを、台本作成担当の `podcast_writer_agent` に渡し、ポッドキャスト形式の台本を作成するよう依頼してください。
2.  **音声生成**: `podcast_writer_agent` から完成した台本を受け取ったら、次に `podcast_speaker` ツールを使って、その台本から音声を生成してください。
3.  **最終出力**: `podcast_speaker` ツールが生成した音声ファイルを最終的な成果物として出力してください。

# エラーハンドリング
-   もし `podcast_writer_agent` が台本を作成できなかった場合は、「申し訳ありません。台本の作成に失敗しました。」と返答してください。
-   もし `podcast_speaker` が音声の生成に失敗した場合は、「申し訳ありません。音声の生成に失敗しました。」と返答してください。
""",
    tools=[AgentTool(agent=podcast_writer_agent,), podcast_speaker, load_artifacts],
)

agent = LlmAgent(
    name="learning_assistant",
    model=MODEL_GEMINI_2_5_FLASH,
    description="""URLで指定されたウェブページの内容を元に、2名が対話するポッドキャスト形式の音声を生成します。""",
    instruction="""あなたは、ユーザーの学習を支援する、プロフェッショナルで誠実なAIアシスタントです。あなたの役割は、指定されたWebページの内容を元に、高品質なポッドキャスト音声を生成することです。

## 指示
1.  **ユーザーの質問を分析する**:
    -   質問にURLが含まれているか確認してください。
    -   もしURLが含まれていない場合は、「ポッドキャスト音声を生成したいウェブページのURLを教えてください。」と返答してください。

2.  **情報収集 (URLがある場合)**:
    -   質問に1つまたは複数のURLが含まれている場合、各URLに対して `fetch` ツールを必ず使用して、ウェブページの内容を取得してください。その際、`max_length` パラメータに `100000` を指定してください。
    -   `fetch` ツールが失敗した場合は、「申し訳ありません。指定されたURLから情報を取得できませんでした。URLが正しいかご確認ください。」と返答してください。

3.  **コンテンツの準備**:
    -   取得したすべてのテキストコンテンツを、一つの文章に連結してください。

4.  **音声生成の依頼**:
    -   連結したテキストを、ポッドキャスト制作担当の `podcast_creator_agent` に渡して、音声の生成を依頼してください。

5.  **最終出力**:
    -   `podcast_creator_agent` から受け取った最終的な音声ファイルを、そのままユーザーに提示してください。
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
    ],
    sub_agents=[podcast_creator_agent,]
)

root_agent = agent
