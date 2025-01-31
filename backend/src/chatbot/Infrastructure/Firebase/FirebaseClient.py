import logging
from typing import Optional

import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.client import Client

logger = logging.getLogger(__name__)

class FirebaseClient:
    """Firebaseクライアントのシングルトンクラス"""
    
    _instance: Optional["FirebaseClient"] = None
    _db: Optional[Client] = None
    _initialized: bool = False

    def __new__(cls) -> "FirebaseClient":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._initialize_firebase()
            self._initialized = True

    def _initialize_firebase(self) -> None:
        """Firebaseの初期化を行う"""
        try:
            # デフォルトの認証情報を使用
            cred = credentials.ApplicationDefault()
            logger.info(f"cred: {cred}")

            # アプリがまだ初期化されていない場合のみ初期化
            if not firebase_admin._apps:
                firebase_admin.initialize_app(cred)
                logger.info("Firebase app initialized successfully")

            # Firestoreクライアントの初期化
            self._db = firestore.client()
            logger.info("Firestore client initialized successfully")

        except Exception as e:
            logger.error(f"Firestore initialization failed: {e}", exc_info=True)
            raise

    @property
    def db(self) -> Client:
        """Firestoreクライアントを取得する"""
        if self._db is None:
            raise RuntimeError("Firestore client is not initialized")
        return self._db

    @classmethod
    def get_instance(cls) -> "FirebaseClient":
        """FirebaseClientのインスタンスを取得する"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance 