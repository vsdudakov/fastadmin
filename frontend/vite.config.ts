import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'
import EnvironmentPlugin from "vite-plugin-environment";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react(), EnvironmentPlugin("all", { prefix: "" })],
  resolve: {
    alias: [{ find: "@", replacement: "/src" }],
  },
  build: {
    rollupOptions: {
        output: {
            dir: '../fastadmin/static/',
            entryFileNames: 'index.min.js',
            assetFileNames: 'index.min.css',
            chunkFileNames: "chunk.min.js",
            manualChunks: undefined,
        }
    },
    target: "es2015",
    lib: {
      entry: "src/main.tsx",
      formats: ["umd"],
      name: "App",
    },
  }
})
