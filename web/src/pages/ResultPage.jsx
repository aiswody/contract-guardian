import { useNavigate } from 'react-router-dom'
import { CATEGORY_LABEL, RISK_LABEL } from '../labels'
import { useFlow } from '../store'

function ClauseCard({ clause }) {
  const { text, category, risk_level, model_risk, confidence, reason } = clause
  return (
    <article className={`clause ${risk_level}`}>
      <div className="clause-head">
        <span className={`badge risk ${risk_level}`}>{RISK_LABEL[risk_level]}</span>
        <span className="badge category">{CATEGORY_LABEL[category] ?? category}</span>
        <span className="conf">확신도 {(confidence * 100).toFixed(0)}%</span>
      </div>
      <p className="clause-text">{text}</p>
      {reason && <p className="reason">감지된 신호: {reason}</p>}
      {risk_level === 'uncertain' && (
        <p className="reason">
          모델의 확신이 낮아 단정하지 않습니다 (모델 판단: {RISK_LABEL[model_risk]}).
          대한법률구조공단(국번없이 132) 등 무료 상담을 활용해보세요.
        </p>
      )}
    </article>
  )
}

export default function ResultPage() {
  const navigate = useNavigate()
  const { result } = useFlow()

  if (!result) {
    navigate('/')
    return null
  }

  const { summary, clauses, disclaimer, model_version } = result
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

      <section className="clauses">
        {sorted.map((c) => <ClauseCard key={c.order_index} clause={c} />)}
      </section>

      <button className="ghost" onClick={() => navigate('/correct')}>내용 수정해서 다시 분석</button>
      <button className="ghost" onClick={() => navigate('/')}>새 계약서 분석</button>
      <footer className="disclaimer">분석 모델: {model_version}</footer>
    </main>
  )
}
