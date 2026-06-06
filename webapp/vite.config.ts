import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// Built app is served by the LAN Python server at /webapp/dist/ (so its own
// assets load relatively), while data + audio come from the server root.
// In `npm run dev`, proxy those root paths to the running Python server :8000.
export default defineConfig({
  base: './',
  plugins: [react(), tailwindcss()],
  server: {
    host: true,
    proxy: {
      '/outputs': { target: 'http://localhost:8000', changeOrigin: true },
      '^/[FP][0-9].*\\.WAV$': { target: 'http://localhost:8000', changeOrigin: true },
    },
  },
})
