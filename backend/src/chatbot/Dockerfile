FROM python:3.11-slim

# タイムゾーンを設定
ENV TZ=Asia/Tokyo

# ここで、コンパイラや geos ライブラリをインストール
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgeos-dev \
 && rm -rf /var/lib/apt/lists/*

# GCPプロジェクトIDとVertex AIのリージョンを設定
# PROJECT_IDはご自身のプロジェクトIDに変更してください
ENV PROJECT_ID=tasktrail-ao
ENV VERTEX_AI_LOCATION=asia-northeast1
ENV GENERATIVE_MODEL_NAME=gemini-1.5-flash-preview-0514
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]