import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/consumo":   "http://localhost:8000",
      "/auth":      "http://localhost:8000",
      "/home":      "http://localhost:8000",
      "/objetivos": "http://localhost:8000",
      "/alertas":   "http://localhost:8000",
      "/factura":   "http://localhost:8000",
      "/ingest":    "http://localhost:8000",
    },
  },
  test: {
    globals: true,
    environment: "jsdom",
    setupFiles: ["./src/setupTests.ts"],
  },
});
