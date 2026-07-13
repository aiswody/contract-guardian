import { BrowserRouter, Route, Routes } from 'react-router-dom'
import CorrectPage from './pages/CorrectPage'
import GuidePage from './pages/GuidePage'
import ResultPage from './pages/ResultPage'
import UploadPage from './pages/UploadPage'
import { FlowProvider } from './store'

export default function App() {
  return (
    <FlowProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<UploadPage />} />
          <Route path="/guide" element={<GuidePage />} />
          <Route path="/correct" element={<CorrectPage />} />
          <Route path="/result" element={<ResultPage />} />
        </Routes>
      </BrowserRouter>
    </FlowProvider>
  )
}
