import { useMemo } from "react";

// Compute a smarter default base:
// - Prefer VITE_API_URL if set.
// - Otherwise, reuse current host but swap to port 8000 (works with forwarded ports e.g., Codespaces).
function computeDefaultBase() {
  if (import.meta.env.VITE_API_URL) return import.meta.env.VITE_API_URL;
  if (typeof window !== "undefined") {
    try {
      const url = new URL(window.location.href);
      url.port = "8000";
      return url.origin;
    } catch {
      return "http://localhost:8000";
    }
  }
  return "http://localhost:8000";
}

const defaultBase = computeDefaultBase();
// Fallback token for local dev to avoid 401s if env not set at runtime.
const defaultToken =
  import.meta.env.VITE_PIPELINE_TOKEN ||
  "fa0df8a6e5a1492f8f6b9d86e7c3a0f4a9a8c7d6e5f4c3b2a1d0e9f8c7b6a5d4";

const DEFAULT_TIMEOUT_MS = Number(import.meta.env.VITE_API_TIMEOUT_MS || 60000);

export function useApi(baseUrl = defaultBase) {
  return useMemo(() => {
    async function request(path, options = {}) {
      const headers = new Headers(options.headers || {});
      if (defaultToken && !headers.has("Authorization")) {
        headers.set("Authorization", `Bearer ${defaultToken}`);
      }

      const controller = new AbortController();
      const timeoutMs = typeof options.timeoutMs === "number" ? options.timeoutMs : DEFAULT_TIMEOUT_MS;
      const timeout = setTimeout(() => controller.abort(), timeoutMs);
      try {
        const response = await fetch(`${baseUrl}${path}`, {
          ...options,
          headers,
          signal: controller.signal,
        });
        if (!response.ok) {
          const message = await response.text();
          throw new Error(message || `Request failed with status ${response.status}`);
        }
        return response.json();
      } catch (err) {
        if (err.name === "AbortError") {
          throw new Error(`Request timed out after ${timeoutMs}ms`);
        }
        throw err;
      } finally {
        clearTimeout(timeout);
      }
    }
    return { request, baseUrl };
  }, [baseUrl]);
}
