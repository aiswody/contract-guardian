import { createClient } from '@supabase/supabase-js'

// 미설정이면 null — 저장/히스토리/피드백 UI가 자동으로 숨겨진다 (비로그인 체험은 그대로 동작)
const url = import.meta.env.VITE_SUPABASE_URL
const anonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

export const supabase = url && anonKey ? createClient(url, anonKey) : null

/** 분석 결과를 저장하고, 화면 조항 순서(order_index) → DB clause id 매핑을 돌려준다. */
export async function saveAnalysis({ result, ocrText, userId, title }) {
  const { data: contract, error: cErr } = await supabase
    .from('contracts')
    .insert({
      user_id: userId,
      title: title || `분석 ${new Date().toLocaleDateString('ko-KR')}`,
      ocr_text: ocrText,
      model_version: result.model_version,
    })
    .select('id')
    .single()
  if (cErr) throw cErr

  const rows = result.clauses.map((c) => ({
    contract_id: contract.id,
    order_index: c.order_index,
    text: c.text,
    category: c.category,
    risk_level: c.risk_level,
    confidence: c.confidence,
    reason: c.reason,
    explanation: c.explanation,
    suggestion: c.suggestion,
  }))
  const { data: saved, error: clErr } = await supabase
    .from('clauses').insert(rows).select('id, order_index')
  if (clErr) throw clErr

  // 누락 결과 저장 (필수 조항 이름 → id 매핑)
  const { data: stds } = await supabase.from('standard_clauses').select('id, name')
  const idByName = Object.fromEntries((stds ?? []).map((s) => [s.name, s.id]))
  const checks = (result.missing ?? [])
    .filter((m) => idByName[m.name])
    .map((m) => ({
      contract_id: contract.id,
      standard_clause_id: idByName[m.name],
      is_present: m.is_present,
      similarity: m.similarity,
    }))
  if (checks.length) await supabase.from('missing_checks').insert(checks)

  const clauseIdByIndex = Object.fromEntries(saved.map((r) => [r.order_index, r.id]))
  return { contractId: contract.id, clauseIdByIndex }
}

/** 조항 판정 피드백 — 재학습 데이터원 (스펙 §5.5) */
export function sendFeedback({ clauseId, userId, verdict }) {
  return supabase.from('feedback').insert({ clause_id: clauseId, user_id: userId, verdict })
}
