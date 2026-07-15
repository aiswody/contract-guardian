import { createContext, useContext, useEffect, useState } from 'react'
import { supabase } from './supabase'

// 업로드 → 교정 → 결과 화면이 공유하는 플로우 상태 + 로그인 세션
const FlowContext = createContext(null)

export function FlowProvider({ children }) {
  const [ocrText, setOcrText] = useState('')
  const [result, setResult] = useState(null)
  const [session, setSession] = useState(null)

  useEffect(() => {
    if (!supabase) return
    supabase.auth.getSession().then(({ data }) => setSession(data.session))
    const { data: sub } = supabase.auth.onAuthStateChange((_e, s) => setSession(s))
    return () => sub.subscription.unsubscribe()
  }, [])

  return (
    <FlowContext.Provider value={{ ocrText, setOcrText, result, setResult, session }}>
      {children}
    </FlowContext.Provider>
  )
}

export function useFlow() {
  return useContext(FlowContext)
}
