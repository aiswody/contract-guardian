import { useEffect, useState } from 'react'
import { Link, Navigate, useParams } from 'react-router-dom'
import { CATEGORY_LABEL, RISK_LABEL } from '../labels'
import { useFlow } from '../store'
import { supabase } from '../supabase'

// 히스토리 — 과거 분석 목록·상세 (재계약 시 비교 용도, 스펙 §3.2)
export function HistoryListPage() {
  const { session } = useFlow()
  const [items, setItems] = useState(null)

  useEffect(() => {
    if (!session) return
    supabase
      .from('contracts')
      .select('id, title, created_at, clauses(risk_level)')
      .order('created_at', { ascending: false })
      .then(({ data }) => setItems(data ?? []))
  }, [session])

  if (!supabase) return <Navigate to="/" replace />
  if (!session) return <Navigate to="/login" replace />

  return (
    <main className="page">
      <header className="hero small"><h1>분석 히스토리</h1></header>
      {items === null && <p className="hint">불러오는 중…</p>}
      {items?.length === 0 && (
        <section className="card">
          <p className="hint">저장된 분석이 없어요. 분석 결과 화면에서 저장을 눌러보세요.</p>
          <Link to="/" className="linkbtn">새 계약서 분석하기</Link>
        </section>
      )}
      {items?.map((c) => {
        const danger = c.clauses.filter((x) => x.risk_level === 'danger').length
        return (
          <Link key={c.id} to={`/history/${c.id}`} className="card history-item">
            <strong>{c.title}</strong>
            <span className="hint">
              {new Date(c.created_at).toLocaleString('ko-KR')} · 조항 {c.clauses.length}건
              {danger > 0 && ` · 불리 가능성 ${danger}건`}
            </span>
          </Link>
        )
      })}
    </main>
  )
}

export function HistoryDetailPage() {
  const { id } = useParams()
  const { session } = useFlow()
  const [contract, setContract] = useState(null)

  useEffect(() => {
    if (!session) return
    supabase
      .from('contracts')
      .select('id, title, created_at, model_version, clauses(*), missing_checks(is_present, similarity, standard_clauses(name, recommended_text))')
      .eq('id', id)
      .single()
      .then(({ data }) => setContract(data))
  }, [id, session])

  if (!supabase) return <Navigate to="/" replace />
  if (!session) return <Navigate to="/login" replace />
  if (!contract) return <main className="page"><p className="hint">불러오는 중…</p></main>

  const order = { danger: 0, uncertain: 1, caution: 2, safe: 3 }
  const sorted = [...contract.clauses].sort(
    (a, b) => order[a.risk_level] - order[b.risk_level])
  const absent = contract.missing_checks.filter((m) => !m.is_present)

  return (
    <main className="page">
      <header className="hero small">
        <h1>{contract.title}</h1>
        <p className="hint">{new Date(contract.created_at).toLocaleString('ko-KR')} · {contract.model_version}</p>
      </header>
      <section className="clauses">
        {sorted.map((c) => (
          <article key={c.id} className={`clause ${c.risk_level}`}>
            <div className="clause-head">
              <span className={`badge risk ${c.risk_level}`}>{RISK_LABEL[c.risk_level]}</span>
              <span className="badge category">{CATEGORY_LABEL[c.category] ?? c.category}</span>
            </div>
            <p className="clause-text">{c.text}</p>
            {c.explanation && <p className="explain">{c.explanation}</p>}
            {c.suggestion && (
              <div className="suggestion"><strong>💬 이렇게 요청해보세요</strong><p>{c.suggestion}</p></div>
            )}
          </article>
        ))}
      </section>
      {absent.length > 0 && (
        <section className="card">
          <h2>이 계약서에 없던 필수 특약 {absent.length}건</h2>
          {absent.map((m) => (
            <div key={m.standard_clauses.name} className="missing-item absent">
              <p><strong>⚠️ {m.standard_clauses.name}</strong></p>
            </div>
          ))}
        </section>
      )}
      <Link to="/history" className="linkbtn">← 목록으로</Link>
    </main>
  )
}
