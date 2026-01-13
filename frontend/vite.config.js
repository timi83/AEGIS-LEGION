import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig(({ mode }) => {
  // Load env file based on `mode` in the current working directory.
  // Set the third parameter to '' to load all env regardless of the `VITE_` prefix.
  // const env = loadEnv(mode, process.cwd(), '') 

  // Hardcoded fallback for now, as we want "Smart Defaults"
  // If user sets VITE_API_URL, we could use it, but Proxy is mainly for local dev.
  // Real prod connection string happens in the Axios setup.

  return {
    plugins: [react()],
    server: {
      proxy: {
        "/api": {
          target: process.env.VITE_API_URL || "http://localhost:8001",
          changeOrigin: true,
          secure: false,
        },
      },
    },
  };
});

