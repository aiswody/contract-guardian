import { createContext, useContext, useState } from 'react'

// 업로드 → 교정 → 결과 화면이 공유하는 플로우 상태
const FlowContext = createContext(null)

export function FlowProvider({ children }) {
  const [ocrText, setOcrText] = useState('')
  const [result, setResult] = useState(null)
  return (
    <FlowContext.Provider value={{ ocrText, setOcrText, result, setResult }}>
      {children}
    </FlowContext.Provider>
  )
}

export function useFlow() {
  return useContext(FlowContext)
}
