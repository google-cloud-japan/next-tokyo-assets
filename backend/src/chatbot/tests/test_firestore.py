import os

from firebase_admin import credentials, firestore, initialize_app


def test_firestore_connection():
    try:
        # Firebase初期化
        
        cred = credentials.Certificate(os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))
        try:
            initialize_app(cred)
        except ValueError:
            # すでに初期化されている場合はスキップ
            pass
        
        # Firestoreクライアントの初期化
        db = firestore.client()
        
        # テストデータの書き込み
        test_data = {
            "test": "データ",
            "timestamp": firestore.SERVER_TIMESTAMP
        }
        
        # テストコレクションに書き込み
        doc_ref = db.collection('test_collection').document()
        doc_ref.set(test_data)
        
        print(f"テストデータの書き込みに成功しました。Document ID: {doc_ref.id}")
        
        # データを読み込んで確認
        doc = doc_ref.get()
        print(f"読み込んだデータ: {doc.to_dict()}")
        
        # テストデータの削除
        doc_ref.delete()
        print("テストデータを削除しました")
        
        return True
        
    except Exception as e:
        print(f"Firestoreテストに失敗しました: {str(e)}")
        return False

if __name__ == "__main__":
    test_firestore_connection() 