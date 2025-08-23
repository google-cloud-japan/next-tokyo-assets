from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool
from trafilatura import extract, fetch_url
from trafilatura.settings import use_config

trafilatura_config = use_config()
trafilatura_config.set("DEFAULT", "EXTRACTION_TIMEOUT", "0")

MODEL_GEMINI_2_5_PRO="gemini-2.5-pro"
MODEL_GEMINI_2_5_FLASH="gemini-2.5-flash"
MODEL_GEMINI_2_5_FLASH_LITE="gemini-2.5-flash-lite"
MODEL_GEMINI_2_5_FLASH_PREVIEW_TTS="gemini-2.5-flash-preview-tts"

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
-   解説者の名前を呼ぶときは "佐藤さん" と呼んでください。

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
    description="""文章を元にポッドキャストの台本制作を指示し、完成した台本を出力します。""",
    instruction="""あなたはポッドキャスト番組のプロデューサーです。あなたの仕事は、与えられた素材（テキスト）を元に、最高の台本を完成させることです。

# 指示
1.  受け取ったテキストを、台本作成担当の `podcast_writer_agent` に渡して、ポッドキャスト形式の台本を作成するよう依頼してください。
2.  `podcast_writer_agent` から完成した台本を受け取ったら、内容を一切変更せず、そのまま出力してください。
3.  もし `podcast_writer_agent` が何らかの理由で台本を作成できなかった場合は、「申し訳ありません。台本の作成中にエラーが発生しました。」とだけ出力してください。
""",
    tools=[AgentTool(agent=podcast_writer_agent,)],
)

def fetch(url: str) -> str:
    """指定されたURLのコンテンツを取得し、マークダウン形式で返却します。

    Args:
        url (str): コンテンツを取得するURL
    
    Returns:
        str: マークダウン形式のURL先のコンテンツ。取得に失敗した場合は、"コンテンツの取得に失敗しました。"を返却します。
    """
    downloaded = fetch_url(url)
    result = extract(downloaded, output_format="markdown", with_metadata=True, config=trafilatura_config)
    if result is None:
        return "コンテンツの取得に失敗しました。"
    return result

agent = LlmAgent(
    name="learning_assistant",
    model=MODEL_GEMINI_2_5_FLASH,
    description="""URLで指定されたウェブページの内容を元に、2名が対話するポッドキャスト形式の台本を生成します。""",
    instruction="""あなたは、ユーザーの学習を支援する、プロフェッショナルで誠実なAIアシスタントです。あなたの役割は、指定されたWebページの内容を元に、魅力的なポッドキャスト台本を生成することです。

## 指示
1.  **ユーザーの質問を分析する**:
    -   質問にURLが含まれているか確認してください。
    -   もしURLが含まれていない場合は、「ポッドキャスト台本を作成したいウェブページのURLを教えてください。」と返答してください。

2.  **情報収集 (URLがある場合)**:
    -   質問に1つまたは複数のURLが含まれている場合、各URLに対して `fetch` ツールを必ず使用して、ウェブページの内容を取得してください。
    -   `fetch` ツールが失敗した場合は、「申し訳ありません。指定されたURLから情報を取得できませんでした。URLが正しいかご確認ください。」と返答してください。

3.  **コンテンツの準備**:
    -   取得したすべてのテキストコンテンツを、一つの文章に連結してください。

4.  **台本作成の依頼**:
    -   連結したテキストを、ポッドキャスト制作担当の `podcast_creator_agent` に渡して、台本の生成を依頼してください。

5.  **最終出力**:
    -   `podcast_creator_agent` から受け取った最終的な台本を、そのままユーザーに提示してください。
""",
    tools=[fetch],
    sub_agents=[podcast_creator_agent,]
)

root_agent = agent
