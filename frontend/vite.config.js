import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Build -> dist/, servi par FastAPI (uvicorn) en production.
// En dev : `npm run dev` (HMR) avec proxy /api vers uvicorn :8000.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": "http://localhost:8000",
    },
  },
  build: {
    outDir: "dist",
    emptyOutDir: true,
  },
});
