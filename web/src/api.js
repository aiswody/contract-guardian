// 모델 서버 API 클라이언트 (스펙 §8)
const BASE = import.meta.env.VITE_API_BASE ?? 'http://127.0.0.1:8600'

async function post(path, body) {
  const res = await fetch(`${BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) {
    const detail = await res.json().catch(() => ({}))
    throw new Error(detail.detail ?? `서버 오류 (HTTP ${res.status})`)
  }
  return res.json()
}

/** 이미지 base64 배열 → OCR 텍스트·분리 초안. 결과는 반드시 교정 화면을 거친다. */
export function requestOcr(imagesBase64, imageFormat) {
  return post('/ocr', { images_base64: imagesBase64, image_format: imageFormat })
}

/** 교정 완료된 텍스트 → 조항 분석 결과 */
export function requestAnalyze(ocrText) {
  return post('/analyze', { ocr_text: ocrText })
}
