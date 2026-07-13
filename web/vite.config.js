import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// history 라우팅 유지 (hash 라우팅 금지 — Capacitor v2 대비, CLAUDE.md)
export default defineConfig({
  plugins: [react()],
})
