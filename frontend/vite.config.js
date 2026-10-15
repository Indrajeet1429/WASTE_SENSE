import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// In live mode the dev server forwards /api to FastAPI (default http://localhost:8000).
export default defineConfig({
  plugins: [react()],
  server: { proxy: { "/api": process.env.VITE_PROXY_TARGET || "http://127.0.0.1:8000" } },
});
