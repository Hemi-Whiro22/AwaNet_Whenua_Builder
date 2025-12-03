export async function awa(path: string, options: any = {}) {
  const base = import.meta.env.VITE_API_URL;
  const res = await fetch(`${base}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  return await res.json();
}
