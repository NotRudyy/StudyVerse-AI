import { defineConfig } from "vitest/config";
import path from "node:path";
import { fileURLToPath } from "node:url";

const configDir = path.dirname(fileURLToPath(import.meta.url));

export default defineConfig({
  resolve: { alias: { "@": path.resolve(configDir, "src") } },
  test: { environment: "jsdom", setupFiles: ["./src/test/setup.ts"], include: ["src/**/*.test.{ts,tsx}"] },
});
