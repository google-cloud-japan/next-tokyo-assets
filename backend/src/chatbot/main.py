"""FastAPI based chatbot application using Vertex AI."""

import logging
import sys
from pathlib import Path

from fastapi import FastAPI

# Add the project root to Python path
project_root = str(Path(__file__).parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from Config.LlmConfig import PROJECT_ID, VERTEX_AI_LOCATION
from Config.LogConfig import setup_logging
from Http.Api.Routes import router

# ロガーの設定
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# FastAPIアプリケーションの初期化
app = FastAPI(title="Chatbot API", description="Vertex AIを使用したチャットボットAPI")

# ルーターの登録
app.include_router(router)

# アプリケーション起動時にロギング設定を行う
setup_logging()
