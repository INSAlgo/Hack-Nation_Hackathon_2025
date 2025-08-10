import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import path from "path";
import { componentTagger } from "lovable-tagger";

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => ({
  server: {
    host: "::",
    port: 8080,
    proxy: {
      // Proxy API requests to Flask backend (use 127.0.0.1 to avoid IPv6/IPv4 issues)
      '/chat': 'http://127.0.0.1:8000',
      '/session': 'http://127.0.0.1:8000',
      '/video': 'http://127.0.0.1:8000',
      // Add more API routes as needed
    },
  },
  plugins: [
    react(),
    mode === 'development' &&
    componentTagger(),
  ].filter(Boolean),
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
}));
