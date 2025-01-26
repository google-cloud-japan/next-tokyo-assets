import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logging():
    """
    ロギングの設定を行う
    - INFOレベル以上のログをファイルに出力
    - ログファイルは10MBごとにローテーション
    - 最大5世代のログファイルを保持
    """
    # ログディレクトリの作成
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # ロガーの取得
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # フォーマッターの作成
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # ファイルハンドラーの設定
    log_file = os.path.join(log_dir, "chatbot.log")
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    # 既存のハンドラーをクリア
    logger.handlers = []

    # ハンドラーの追加
    logger.addHandler(file_handler)

    # デバッグ用にコンソール出力も残す
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
