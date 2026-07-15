import { useState } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'
import { CATEGORY_LABEL, RISK_LABEL } from '../labels'
import { useFlow } from '../store'
import { saveAnalysis, sendFeedback, supabase } from '../supabase'

function FeedbackButtons({ clauseId, userId }) {
  const [sent, setSent] = useState(null)
  if (!clauseId) return null
  if (sent) return <p className="hint">피드백 감사합니다 — 모델 개선에 사용돼요. ({sent === 'helpful' ? '도움됨' : '판정 이상'})</p>
  async function send(verdict) {
    await sendFeedback({ clauseId, userId, verdict })
    setSent(verdict)
  }
  return (
    <div className="feedback">
      <span className="hint">이 판정이 어땠나요?</span>
      <button className="navbtn" onClick={() => send('helpful')}>👍 도움됨</button>
      <button className="navbtn" onClick={() => send('wrong')}>👎 판정이 이상함</button>
    </div>
  )
}

function ClauseCard({ clause, clauseId, userId }) {
  const { text, category, risk_level, model_risk, confidence, reason,
          explanation, suggestion } = clause
  return (
    <article className={`clause ${risk_level}`}>
      <div className="clause-head">
        <span className={`badge risk ${risk_level}`}>{RISK_LABEL[risk_level]}</span>
        <span className="badge category">{CATEGORY_LABEL[category] ?? category}</span>
        <span className="conf">확신도 {(confidence * 100).toFixed(0)}%</span>
      </div>
      <p className="clause-text">{text}</p>
      {reason && <p className="reason">감지된 신호: {reason}</p>}
      {explanation && <p className="explain">{explanation}</p>}
      {suggestion && (
        <div className="suggestion">
          <strong>💬 이렇게 요청해보세요</strong>
          <p>{suggestion}</p>
        </div>
      )}
      {risk_level === 'uncertain' && !(reason ?? '').includes('상충') && (
        <p className="reason">
          모델의 확신이 낮아 단정하지 않습니다 (모델 판단: {RISK_LABEL[model_risk]}).
        </p>
      )}
      <FeedbackButtons clauseId={clauseId} userId={userId} />
    </article>
  )
}

function MissingSection({ missing }) {
  if (!missing?.length) return null
  const absent = missing.filter((m) => !m.is_present)
  return (
    <section className="card">
      <h2>계약서에 없는 필수 특약 {absent.length ? `${absent.length}건` : ''}</h2>
      {absent.length === 0 && <p className="hint">필수 특약 7종이 모두 확인됐어요. 👍</p>}
      {missing.map((m) => (
        <div key={m.name} className={`missing-item ${m.is_present ? 'ok' : 'absent'}`}>
          <p><strong>{m.is_present ? '✅' : '⚠️'} {m.name}</strong></p>
          {!m.is_present && (
            <>
              <p className="hint">{m.description}</p>
              <div className="suggestion">
                <strong>📝 이 문구를 추가해달라고 요청하세요</strong>
                <p>{m.recommended_text}</p>
              </div>
            </>
          )}
        </div>
      ))}
      <p className="hint">
        ※ 표현이 특이하면 있는 조항도 누락 가능성으로 표시될 수 있어요. 목록은 확인용 참고입니다.
      </p>
    </section>
  )
}

export default function ResultPage() {
  const navigate = useNavigate()
  const { result, ocrText, session } = useFlow()
  const [saved, setSaved] = useState(null)   // { contractId, clauseIdByIndex }
  const [saving, setSaving] = useState(false)
  const [saveError, setSaveError] = useState(null)

  // 새로고침 등으로 결과 상태가 없으면 처음으로 (렌더 중 navigate 호출은 화면이 죽는다)
  if (!result) return <Navigate to="/" replace />

  async function handleSave() {
    setSaving(true)
    setSaveError(null)
    try {
      const title = window.prompt('저장할 이름을 입력하세요 (예: OO빌 원룸 전세)') || undefined
      const res = await saveAnalysis({ result, ocrText, userId: session.user.id, title })
      setSaved(res)
    } catch (e) {
      setSaveError(e.message)
    } finally {
      setSaving(false)
    }
  }

  const { summary, clauses, missing, disclaimer, model_version } = result
  const order = { danger: 0, uncertain: 1, caution: 2, safe: 3 }
  const sorted = [...clauses].sort((a, b) => order[a.risk_level] - order[b.risk_level])

  return (
    <main className="page">
      <header className="hero small">
        <h1>3. 분석 결과</h1>
        <p className="disclaimer-top">{disclaimer}</p>
      </header>

      <section className="summary">
        <div className="stat danger"><strong>{summary.danger}</strong><span>불리 가능성</span></div>
        <div className="stat caution"><strong>{summary.caution}</strong><span>주의</span></div>
        <div className="stat uncertain"><strong>{summary.uncertain}</strong><span>확인 필요</span></div>
        <div className="stat safe"><strong>{summary.safe}</strong><span>통상 조항</span></div>
      </section>

      {supabase && (
        <section className="card">
          {!session && (
            <p className="hint">
              결과를 저장하고 다시 보려면 <Link to="/login">로그인</Link>하세요.
              저장하면 조항별 피드백도 남길 수 있어요.
            </p>
          )}
          {session && !saved && (
            <>
              <button className="primary" disabled={saving} onClick={handleSave}>
                {saving ? '저장 중…' : '이 분석 결과 저장하기'}
              </button>
              <p className="hint">저장하면 조항마다 판정 피드백(👍/👎)을 남길 수 있어요.</p>
            </>
          )}
          {saved && <p className="hint">✅ 저장됐어요. 아래 조항마다 판정 피드백을 남길 수 있고, <Link to="/history">히스토리</Link>에서 다시 볼 수 있어요.</p>}
          {saveError && <p className="error">{saveError}</p>}
        </section>
      )}

      <section className="clauses">
        {sorted.map((c) => (
          <ClauseCard
            key={c.order_index}
            clause={c}
            clauseId={saved?.clauseIdByIndex?.[c.order_index]}
            userId={session?.user?.id}
          />
        ))}
      </section>

      <MissingSection missing={missing} />

      <button className="ghost" onClick={() => navigate('/correct')}>내용 수정해서 다시 분석</button>
      <button className="ghost" onClick={() => navigate('/')}>새 계약서 분석</button>
      <footer className="disclaimer">분석 모델: {model_version}</footer>
    </main>
  )
}
