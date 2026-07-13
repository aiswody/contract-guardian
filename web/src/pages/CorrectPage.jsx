import { useState } from 'react'
import { Navigate, useNavigate } from 'react-router-dom'
import { requestAnalyze } from '../api'
import { useFlow } from '../store'

// OCR 교정 화면 — 스펙 §9-4: 교정을 거치지 않은 텍스트는 분석하지 않는다 (강제 노출)
export default function CorrectPage() {
  const navigate = useNavigate()
  const { ocrText, setOcrText, setResult } = useFlow()
  const [text, setText] = useState(ocrText)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  if (!ocrText) return <Navigate to="/" replace />

  async function handleAnalyze() {
    setLoading(true)
    setError(null)
    try {
      setOcrText(text)
      const result = await requestAnalyze(text)
      setResult(result)
      navigate('/result')
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="page">
      <header className="hero small">
        <h1>2. 읽어낸 내용을 확인해주세요</h1>
        <p>사진에서 잘못 읽힌 글자가 있으면 직접 고쳐주세요. 잘못 읽힌 채 분석하면 결과도 틀립니다.</p>
      </header>

      <section className="card">
        <textarea
          rows={14}
          value={text}
          onChange={(e) => setText(e.target.value)}
          spellCheck={false}
        />
        <button className="primary" disabled={loading || !text.trim()} onClick={handleAnalyze}>
          {loading ? '조항을 분석하는 중…' : '이 내용으로 분석하기'}
        </button>
        <button className="ghost" onClick={() => navigate('/')}>처음으로</button>
      </section>

      {loading && (
        <section className="progress card">
          <p>① 조항 분리 → ② 위험도 분석 → ③ 결과 정리</p>
          <p className="hint">모델이 조항을 하나씩 읽고 있습니다…</p>
        </section>
      )}
      {error && <p className="error">{error}</p>}
    </main>
  )
}
