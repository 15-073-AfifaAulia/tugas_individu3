import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      // Setiap request ke /api akan diteruskan ke Backend Pyramid
      '/api': {
        target: 'http://localhost:6543',
        changeOrigin: true,
      }
    }
  }
})