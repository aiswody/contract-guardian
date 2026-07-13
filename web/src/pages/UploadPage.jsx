import { useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { requestOcr } from '../api'
import { useFlow } from '../store'

function fileToBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(reader.result.split(',')[1]) // data: 프리픽스 제거
    reader.onerror = reject
    reader.readAsDataURL(file)
  })
}

export default function UploadPage() {
  const navigate = useNavigate()
  const { setOcrText } = useFlow()
  const fileInput = useRef(null)
  const [pasted, setPasted] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  async function handleFiles(files) {
    if (!files?.length) return
    setLoading(true)
    setError(null)
    try {
      const images = await Promise.all([...files].map(fileToBase64))
      const format = files[0].type.includes('png') ? 'png' : 'jpg'
      const { text } = await requestOcr(images, format)
      setOcrText(text)
      navigate('/correct')
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  function handlePaste() {
    if (!pasted.trim()) return
    setOcrText(pasted.trim())
    navigate('/correct')
  }

  return (
    <main className="page">
      <header className="hero">
        <h1>계약서 지킴이</h1>
        <p>서명하기 전 5분, 전월세 계약서의 특약을 확인하세요.</p>
      </header>

      <section className="card">
        <h2>1. 계약서 사진 올리기</h2>
        <p className="hint">특약사항 부분이 잘 보이게 찍어주세요. 여러 장도 됩니다.</p>
        <input
          ref={fileInput}
          type="file"
          accept="image/jpeg,image/png"
          multiple
          hidden
          onChange={(e) => handleFiles(e.target.files)}
        />
        <button className="primary" disabled={loading} onClick={() => fileInput.current.click()}>
          {loading ? '글자를 읽는 중…' : '사진 선택 / 촬영'}
        </button>
      </section>

      <div className="divider">또는</div>

      <section className="card">
        <h2>특약 내용 직접 붙여넣기</h2>
        <textarea
          rows={6}
          placeholder={'예)\n1. 임차인은 전입신고를 하지 않기로 한다.\n2. 관리비는 별도로 한다.'}
          value={pasted}
          onChange={(e) => setPasted(e.target.value)}
        />
        <button className="primary" disabled={!pasted.trim() || loading} onClick={handlePaste}>
          이 내용으로 진행
        </button>
      </section>

      {error && <p className="error">{error}</p>}
      <footer className="disclaimer">본 서비스는 참고 정보를 제공하며 법률 자문이 아닙니다.</footer>
    </main>
  )
}
