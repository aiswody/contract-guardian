import { BrowserRouter, Link, Route, Routes } from 'react-router-dom'
import CorrectPage from './pages/CorrectPage'
import GuidePage from './pages/GuidePage'
import { HistoryDetailPage, HistoryListPage } from './pages/HistoryPage'
import LoginPage from './pages/LoginPage'
import ResultPage from './pages/ResultPage'
import UploadPage from './pages/UploadPage'
import { FlowProvider, useFlow } from './store'
import { supabase } from './supabase'

function Nav() {
  const { session } = useFlow()
  return (
    <nav className="topnav">
      <Link to="/">🛡️ 계약서 지킴이</Link>
      <div>
        <Link to="/guide">가이드</Link>
        {supabase && session && <Link to="/history">히스토리</Link>}
        {supabase && (session
          ? <button className="navbtn" onClick={() => supabase.auth.signOut()}>로그아웃</button>
          : <Link to="/login">로그인</Link>)}
      </div>
    </nav>
  )
}

export default function App() {
  return (
    <FlowProvider>
      <BrowserRouter>
        <Nav />
        <Routes>
          <Route path="/" element={<UploadPage />} />
          <Route path="/guide" element={<GuidePage />} />
          <Route path="/correct" element={<CorrectPage />} />
          <Route path="/result" element={<ResultPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/history" element={<HistoryListPage />} />
          <Route path="/history/:id" element={<HistoryDetailPage />} />
        </Routes>
      </BrowserRouter>
    </FlowProvider>
  )
}