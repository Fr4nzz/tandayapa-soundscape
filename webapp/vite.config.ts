import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// Public build for GitHub Pages at https://fr4nzz.github.io/tandayapa-soundscape/app/.
// Detection JSON is bundled (public/data); audio streams from Cloudflare R2.
export default defineConfig({
  base: '/tandayapa-soundscape/app/',
  plugins: [react(), tailwindcss()],
  server: { host: true },
})
