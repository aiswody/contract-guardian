"""계약서 지킴이 모델 서버 (스펙 §8).

POST /analyze : 텍스트(교정 완료) → 조항 분리 → 위험도/카테고리 분류
POST /ocr     : 이미지 OCR (CLOVA 설정 시 — 미설정이면 503, 텍스트 직접 입력 경로 사용)
GET  /health, /model-info

원칙: OCR 결과는 사용자 교정을 거친 텍스트만 분석한다 (스펙 §9-4).
/analyze의 image_urls 경로는 프론트의 교정 화면을 거친 뒤에만 쓰도록 프론트에서 강제한다.
로컬 실행: cd model-server && uvicorn app.main:app --reload
"""
import os
from contextlib import asynccontextmanager
from pathlib import Path

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

from .explain import get_explainer
from .inference import MODEL_VERSION, THRESHOLD, Pipeline
from .missing import MissingDetector
from .ocr import OcrNotConfigured, run_ocr
from .schemas import AnalyzeRequest, AnalyzeResponse, OcrRequest, Summary
from .segmentation import segment

pipeline: Pipeline | None = None
missing_detector: MissingDetector | None = None
explainer = get_explainer()


@asynccontextmanager
async def lifespan(app: FastAPI):
    global pipeline, missing_detector
    pipeline = Pipeline()                # 분류 모델 — 기동 시 1회 로드
    missing_detector = MissingDetector() # 임베딩 모델 — 기동 시 1회 로드
    yield


app = FastAPI(title="Contract Guardian Model Server", lifespan=lifespan)

# 프론트(Vite dev 서버·Vercel)에서의 브라우저 호출 허용
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/model-info")
def model_info():
    return {
        "model_version": MODEL_VERSION,
        "backbone": "klue/roberta-base",
        "risk_threshold": THRESHOLD,
        "metrics_note": "test(34문장): 위험도 danger Recall 0.636 / 카테고리 Macro-F1 0.967 — ml/reports/week3_results.md",
    }


@app.post("/ocr")
def ocr(req: OcrRequest):
    """OCR만 수행해 교정 화면용 텍스트·분리 초안을 돌려준다 (스펙 §8).

    이 결과는 반드시 사용자 교정을 거친 뒤 /analyze로 보내야 한다 (스펙 §9-4).
    """
    if not (req.image_urls or req.images_base64):
        raise HTTPException(422, "image_urls 또는 images_base64가 필요합니다.")
    try:
        text = run_ocr(req.image_urls, req.images_base64, req.image_format)
    except OcrNotConfigured:
        raise HTTPException(503, "OCR 미설정 (CLOVA_OCR_URL/SECRET 필요). 텍스트 직접 입력 경로를 사용하세요.")
    except httpx.HTTPStatusError as e:
        raise HTTPException(502, f"CLOVA OCR 오류: HTTP {e.response.status_code}")
    return {"text": text, "segments": segment(text)}


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(req: AnalyzeRequest):
    if not req.ocr_text:
        if req.image_urls:
            raise HTTPException(503, "이미지 경로는 OCR 설정 후 지원. 교정된 텍스트(ocr_text)를 보내세요.")
        raise HTTPException(422, "ocr_text가 필요합니다.")

    clauses_text = segment(req.ocr_text)
    if not clauses_text:
        raise HTTPException(422, "분리 가능한 조항이 없습니다. 입력 텍스트를 확인하세요.")

    clauses = pipeline.analyze_clauses(clauses_text)
    missing, protective_sim = missing_detector.detect(clauses_text)

    # 교차 검증: 권장 필수 특약과 강하게 매칭(보호 조항으로 보임)되는데 모델이
    # 위험/주의로 판정했고 위험 신호 패턴도 없다면 — 판정 상충이므로 확인 필요로 강등.
    # (신호가 잡힌 조항은 강등하지 않는다: 임베딩은 부정어에 둔감해 위장 조항 위험이 있음)
    from .missing import SIM_THRESHOLD as PROTECTIVE_SIM
    for clause, sim in zip(clauses, protective_sim):
        if (clause["risk_level"] in ("danger", "caution")
                and not clause["reason"] and sim >= PROTECTIVE_SIM):
            clause["risk_level"] = "uncertain"
            clause["reason"] = f"권장 필수 특약과 유사 (유사도 {sim:.0%}) — 모델 판정과 상충"

    for clause in clauses:  # 판정 완료 후 설명 부착 — 설명은 판별에 관여하지 않는다
        clause.update(explainer.explain(clause) or {})
    counts = {k: sum(1 for c in clauses if c["risk_level"] == k)
              for k in ("danger", "caution", "safe", "uncertain")}
    return AnalyzeResponse(
        contract_id=req.contract_id,
        model_version=MODEL_VERSION,
        clauses=clauses,
        missing=missing,
        summary=Summary(total=len(clauses), **counts),
    )
