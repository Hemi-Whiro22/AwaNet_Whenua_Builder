import { useMemo } from "react";

const defaultBase = import.meta.env.VITE_API_URL || "http://localhost:8000";

export function useApi(baseUrl = defaultBase) {
  return useMemo(() => {
    async function request(path, options = {}) {
      const response = await fetch(`${baseUrl}${path}`, options);
      if (!response.ok) {
        const message = await response.text();
        throw new Error(message || `Request failed with status ${response.status}`);
      }
      return response.json();
    }
    return { request, baseUrl };
  }, [baseUrl]);
}
