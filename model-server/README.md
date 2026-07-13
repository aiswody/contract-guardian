# model-server — FastAPI 추론 서버

## 로컬 실행

```bash
cd model-server
pip install -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cpu
uvicorn app.main:app --reload          # http://127.0.0.1:8000/docs
```

모델 아티팩트는 git에 없다. `models/` 아래에 다음 구조가 필요:
`risk_model_v2/best/`, `category_model/best/` (학습: `ml/scripts/train_local.py`, `ml/notebooks/`).

## 엔드포인트 (스펙 §8)

| 경로 | 설명 |
|---|---|
| `POST /analyze` | `{ocr_text}` → 조항 분리 → 위험도/카테고리 분류. 응답에 `uncertain` 판정·근거 신호·법률 자문 아님 고지 포함 |
| `POST /ocr` | CLOVA OCR (환경변수 `CLOVA_OCR_SECRET` 설정 시 — 미설정이면 503) |
| `GET /health`, `GET /model-info` | 상태·모델 버전/threshold 노출 |

## 설계 메모

- **판별은 모델, 설명은 LLM** — 이 서버의 분류 경로에 LLM 없음. LLM 설명 생성은 6주차에 별도 라우트로 추가.
- **threshold 0.7** (3주차 튜닝): confidence 미만이면 `uncertain`으로 강등, 원 판정(`model_risk`)과 확신도는 함께 반환.
- **reason 필드**: 가이드라인 기반 위험 신호 패턴(`app/patterns.py`) — 모델 판정과 독립적인 근거 표시용.
- OCR 텍스트는 **사용자 교정 후에만** `/analyze`로 보낼 것 (스펙 §9-4, 프론트에서 강제).

## Docker

```bash
docker build -t contract-guardian-server .
docker run -p 8080:8080 contract-guardian-server
```
