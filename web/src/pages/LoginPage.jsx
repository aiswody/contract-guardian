import { useState } from 'react'
import { Navigate } from 'react-router-dom'
import { supabase } from '../supabase'
import { useFlow } from '../store'

// 이메일 매직링크 로그인 — 비밀번호 없이 메일의 링크로 인증 (무료, Supabase Auth)
export default function LoginPage() {
  const { session } = useFlow()
  const [email, setEmail] = useState('')
  const [sent, setSent] = useState(false)
  const [sending, setSending] = useState(false)
  const [error, setError] = useState(null)

  if (!supabase) return <Navigate to="/" replace />
  if (session) return <Navigate to="/history" replace />

  async function handleLogin(e) {
    e.preventDefault()
    if (sending) return  // 중복 요청 차단 (발송 제한에 걸려 알 수 없는 에러가 뜨는 원인)
    setSending(true)
    setError(null)
    const { error } = await supabase.auth.signInWithOtp({
      email,
      options: { emailRedirectTo: window.location.origin },
    })
    setSending(false)
    if (error) {
      // 빈 응답('{}')이나 발송 제한은 사용자 언어로 안내
      const msg = error.message && error.message !== '{}'
        ? error.message
        : '잠시 후 다시 시도해주세요. 같은 메일로는 60초에 한 번만 보낼 수 있어요.'
      setError(msg)
    } else {
      setSent(true)
    }
  }

  return (
    <main className="page">
      <header className="hero small">
        <h1>로그인</h1>
        <p>분석 결과를 저장하고 다시 보려면 로그인하세요. 비밀번호 없이 이메일 링크로 로그인합니다.</p>
      </header>
      <section className="card">
        {sent ? (
          <p>✉️ <strong>{email}</strong>로 로그인 링크를 보냈어요. 메일함을 확인해주세요.</p>
        ) : (
          <form onSubmit={handleLogin} className="card" style={{ border: 'none', padding: 0 }}>
            <input
              type="email"
              required
              placeholder="이메일 주소"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="text-input"
            />
            <button className="primary" type="submit" disabled={sending}>
              {sending ? '보내는 중…' : '로그인 링크 받기'}
            </button>
          </form>
        )}
        {error && <p className="error">{error}</p>}
      </section>
    </main>
  )
}
