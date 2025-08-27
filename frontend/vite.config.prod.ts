import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  base: '/Telemetry-Analytics-Dashboard-for-Smart-Drilling-Machines/',
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
  },
  define: {
    // Define environment variables for production
    __PROD_API_BASE_URL__: JSON.stringify(process.env.VITE_API_BASE_URL || 'http://localhost:8000'),
  },
})