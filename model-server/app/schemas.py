"""요청/응답 스키마 (스펙 §8)."""
from pydantic import BaseModel, Field

DISCLAIMER = ("본 분석은 참고 정보이며 법률 자문이 아닙니다. "
              "중요한 판단은 대한법률구조공단(132) 등 전문가 상담을 이용하세요.")


class AnalyzeRequest(BaseModel):
    contract_id: str | None = None
    ocr_text: str | None = Field(None, description="교정 완료된 계약서/특약 텍스트")
    image_urls: list[str] | None = Field(None, description="OCR 미수행 이미지 URL (OCR 설정 시)")


class Clause(BaseModel):
    order_index: int
    text: str
    category: str
    risk_level: str          # safe | caution | danger | uncertain
    model_risk: str
    confidence: float
    reason: str | None


class Summary(BaseModel):
    total: int
    danger: int
    caution: int
    safe: int
    uncertain: int


class AnalyzeResponse(BaseModel):
    contract_id: str | None
    model_version: str
    clauses: list[Clause]
    missing: list[dict] = []   # 6주차: 누락 조항 탐지
    summary: Summary
    disclaimer: str = DISCLAIMER


class OcrRequest(BaseModel):
    image_urls: list[str] | None = None
    images_base64: list[str] | None = None
    image_format: str = "jpg"
