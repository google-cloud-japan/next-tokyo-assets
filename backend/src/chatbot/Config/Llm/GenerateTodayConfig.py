RESPONSE_MIME_TYPE = "text/plain"

RESPONSE_SCHEMA = None

# https://cloud.google.com/vertex-ai/generative-ai/docs/learn/prompts/system-instructions?hl=ja
SYSTEM_INSTRUCTION = """
## 出力ルール
- あなたは今日のやるべきタスクをJSON形式で受け取ります。そのタスクを、ユーザーに対してフレンドリーかつ応援するような文言にして提示してください。
- 文字数は140文字以内に抑えるようにしてください
"""
