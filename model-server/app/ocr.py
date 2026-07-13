"""CLOVA General OCR 클라이언트 (스펙 §5.4).

- 글자 추출만 사용한다 — enableTableDetection=False로 표 추출(건당 22원) 차단.
- 입력: 이미지 URL(Supabase signed URL 등) 또는 base64 데이터.
- 출력: lineBreak 정보를 살려 줄바꿈을 복원한 전체 텍스트
  (조항 세그멘테이션이 줄바꿈을 분리 신호로 쓰기 때문).
- 환경변수: CLOVA_OCR_URL, CLOVA_OCR_SECRET (model-server/.env — git 미포함)
"""
import os
import time
import uuid

import httpx


class OcrNotConfigured(Exception):
    pass


def _config() -> tuple[str, str]:
    url, secret = os.environ.get("CLOVA_OCR_URL"), os.environ.get("CLOVA_OCR_SECRET")
    if not url or not secret:
        raise OcrNotConfigured
    return url, secret


def run_ocr(image_urls: list[str] | None = None,
            images_base64: list[str] | None = None,
            image_format: str = "jpg") -> str:
    url, secret = _config()

    images = []
    for u in image_urls or []:
        images.append({"format": image_format, "name": f"img{len(images)}", "url": u})
    for d in images_base64 or []:
        images.append({"format": image_format, "name": f"img{len(images)}", "data": d})
    if not images:
        raise ValueError("이미지가 없습니다")

    payload = {
        "version": "V2",
        "requestId": str(uuid.uuid4()),
        "timestamp": int(time.time() * 1000),
        "images": images,
        "enableTableDetection": False,
    }
    resp = httpx.post(url, json=payload, headers={"X-OCR-SECRET": secret}, timeout=30)
    resp.raise_for_status()

    pages = []
    for img in resp.json().get("images", []):
        if img.get("inferResult") == "ERROR":
            raise RuntimeError(f"OCR 실패: {img.get('message')}")
        parts = []
        for field in img.get("fields", []):
            parts.append(field["inferText"])
            parts.append("\n" if field.get("lineBreak") else " ")
        pages.append("".join(parts).strip())
    return "\n".join(pages)
