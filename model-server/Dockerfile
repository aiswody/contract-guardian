# 계약서 지킴이 모델 서버 — Cloud Run 배포용 (스펙 §6)
# 모델 아티팩트(약 900MB)를 이미지에 포함하는 단순 구성.
# 빌드 전 model-server/models/ 아래에 risk_model_v2/, category_model/ 이 있어야 한다.
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    --extra-index-url https://download.pytorch.org/whl/cpu

COPY app ./app
COPY models ./models
ENV MODEL_DIR=/app/models

# Cloud Run은 PORT 환경변수를 주입한다
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
