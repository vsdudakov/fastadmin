import { defineConfig, UserConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'
import EnvironmentPlugin from "vite-plugin-environment";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react(), EnvironmentPlugin("all", { prefix: "" })],
  test: {
    setupFiles: ["src/test-setup.ts"],
    coverage: {
      provider: "v8",
      reporter: ["text", "text-summary", "html", "lcov"],
      include: ["src/**/*.{ts,tsx}"],
      exclude: [
        "src/**/*.test.{ts,tsx}",
        "src/test-setup.ts",
        "src/main.tsx",
        "src/interfaces/user.ts",
        "src/vite-env.d.ts",
      ],
      thresholds: {
        statements: 96,
        branches: 81,
        functions: 91,
        lines: 96,
      },
    },
  },
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
} as UserConfig)
