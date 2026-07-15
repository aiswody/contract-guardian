import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'
import { VitePWA } from 'vite-plugin-pwa'

// history 라우팅 유지 (hash 라우팅 금지 — Capacitor v2 대비, CLAUDE.md)
export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      manifest: {
        name: '계약서 지킴이',
        short_name: '계약서지킴이',
        description: '서명하기 전 5분, 전월세 계약서의 특약을 확인하세요',
        lang: 'ko',
        theme_color: '#2563eb',
        background_color: '#f6f7f9',
        display: 'standalone',
        icons: [
          { src: '/pwa-192.png', sizes: '192x192', type: 'image/png' },
          { src: '/pwa-512.png', sizes: '512x512', type: 'image/png' },
        ],
      },
      workbox: {
        // API 응답(분석 결과)은 캐시하지 않는다 — 항상 최신 모델 판정
        navigateFallbackDenylist: [/^\/api/],
      },
    }),
  ],
})
