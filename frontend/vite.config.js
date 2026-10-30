import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// Geliştirmede /api istekleri Django'ya (8000) yönlendirilir; CORS gerekmez.
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': 'http://localhost:8000',
    },
  },
})
