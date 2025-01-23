FROM python:3.11-slim

# タイムゾーンを設定
ENV TZ=Asia/Tokyo

# GCPプロジェクトIDとVertex AIのリージョンを設定
# PROJECT_IDはご自身のプロジェクトIDに変更してください
ENV PROJECT_ID=tasktrail-ao
ENV VERTEX_AI_LOCATION=asia-northeast1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]