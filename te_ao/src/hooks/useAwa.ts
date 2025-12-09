export async function awa(path: string, options: any = {}) {
  const base = import.meta.env.VITE_API_URL;
  const token =
    import.meta.env.VITE_PIPELINE_TOKEN ||
    "fa0df8a6e5a1492f8f6b9d86e7c3a0f4a9a8c7d6e5f4c3b2a1d0e9f8c7b6a5d4";
  const headers = new Headers(options.headers || {});
  headers.set("Content-Type", "application/json");
  if (token && !headers.has("Authorization")) {
    headers.set("Authorization", `Bearer ${token}`);
  }
  const res = await fetch(`${base}${path}`, {
    headers,
    ...options,
  });
  return await res.json();
}
