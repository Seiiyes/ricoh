import path from "path"
import react from "@vitejs/plugin-react"
import { defineConfig } from "vite"

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    port: 5173,
    watch: {
      ignored: [
        '**/backend/**',
        '**/node_modules/**',
        '**/.git/**',
        '**/docs/**',
        '**/backups/**'
      ]
    }
  },
  optimizeDeps: {
    exclude: ['backend']
  }
})