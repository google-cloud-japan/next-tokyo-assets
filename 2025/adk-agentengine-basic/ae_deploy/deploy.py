import vertexai
from google.adk.agents import config_agent_utils
from vertexai.preview.reasoning_engines import AdkApp
from vertexai import agent_engines
import os

# 環境変数などからプロジェクト ID とロケーションを設定
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT")
LOCATION = "us-central1"

# プロジェクト内に存在する GCS バケット名を指定
STAGING_BUCKET = f"gs://{PROJECT_ID}-agent-engine-staging"

# Vertex AI を初期化
vertexai.init(project=PROJECT_ID, location=LOCATION, staging_bucket=STAGING_BUCKET)

agent = config_agent_utils.from_config("./root_agent.yaml")
app = AdkApp(agent=agent)

remote_agent = agent_engines.create(
    app,
    requirements=["google-cloud-aiplatform[agent_engines,adk]", "trafilatura"],
    extra_packages=["."]
)

print(f"Deployed agent: {remote_agent.resource_name}")