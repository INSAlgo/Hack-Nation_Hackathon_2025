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
  // Build optimization: split large vendor chunks to stay below 500 kB each.
  build: {
    // Adjust (not hide) warning threshold after meaningful splitting.
    chunkSizeWarningLimit: 700,
    rollupOptions: {
      output: {
        // Fine‑grained manual chunking; ensures heavy libs are cached independently.
        manualChunks(id: string) {
          if (id.includes('node_modules')) {
            if (id.includes('react-router-dom') || id.includes('react-dom') || id.includes('react/jsx-runtime')) {
              return 'react-core';
            }
            if (id.includes('@radix-ui')) {
              return 'radix-ui';
            }
            if (id.includes('recharts')) {
              return 'charts';
            }
            if (id.includes('react-markdown') || id.includes('remark-gfm')) {
              return 'markdown';
            }
            if (id.includes('@tanstack/react-query')) {
              return 'react-query';
            }
            if (id.includes('lucide-react')) {
              return 'icons';
            }
          }
          return undefined; // default chunking
        },
      },
    },
  },
}));
