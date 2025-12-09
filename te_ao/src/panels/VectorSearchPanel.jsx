import { useState } from "react";
import { useApi } from "../hooks/useApi.js";

export default function VectorSearchPanel() {
  const { request } = useApi();
  const [text, setText] = useState("");
  const [topK, setTopK] = useState(5);
  const [history, setHistory] = useState([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [recent, setRecent] = useState([]);

  const handleEmbed = async () => {
    setError("");
    if (!text.trim()) {
      setError("Add text first.");
      return;
    }
    setBusy(true);
    try {
      const result = await request("/vector/embed", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      });
      setHistory((prev) => [{ ...result, kind: "embed" }, ...prev].slice(0, 10));
    } catch (err) {
      setError(err.message || "Embed failed.");
    } finally {
      setBusy(false);
    }
  };

  const handleSearch = async () => {
    setError("");
    if (!text.trim()) {
      setError("Add a query first.");
      return;
    }
    setBusy(true);
    try {
      const result = await request("/vector/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: text, top_k: topK, rerank: true }),
      });
      setHistory((prev) => [{ ...result, kind: "search" }, ...prev].slice(0, 10));
    } catch (err) {
      setError(err.message || "Search failed.");
    } finally {
      setBusy(false);
    }
  };

  const loadRecent = async () => {
    setError("");
    setBusy(true);
    try {
      const result = await request("/vector/recent");
      setRecent(result.entries || []);
    } catch (err) {
      setError(err.message || "Recent fetch failed.");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-6 shadow-lg shadow-black/30">
      <h2 className="text-xl font-semibold text-emerald-200">Vector Search</h2>
      <p className="mt-2 text-sm text-slate-300">Embed and search via /vector/embed + /vector/search.</p>
      <div className="mt-4 flex flex-col gap-3">
        <textarea
          className="min-h-[120px] w-full rounded-lg border border-slate-800 bg-slate-950/60 p-3 text-slate-100"
          placeholder="Enter text to embed or search..."
          value={text}
          onChange={(event) => setText(event.target.value)}
        />
        <div className="flex items-center gap-3 text-sm text-slate-200">
          <label className="flex items-center gap-2">
            Top K
            <input
              type="number"
              min="1"
              max="20"
              value={topK}
              onChange={(event) => setTopK(Number(event.target.value))}
              className="w-16 rounded border border-slate-700 bg-slate-900 px-2 py-1 text-slate-100"
            />
          </label>
          {error && <span className="text-rose-300">{error}</span>}
        </div>
        <div className="flex flex-wrap gap-2">
          <button
            className="rounded-lg bg-emerald-600 px-3 py-2 text-sm font-semibold text-white transition hover:bg-emerald-500 disabled:opacity-60"
            onClick={handleEmbed}
            disabled={busy}
          >
            Embed
          </button>
          <button
            className="rounded-lg bg-blue-600 px-3 py-2 text-sm font-semibold text-white transition hover:bg-blue-500 disabled:opacity-60"
            onClick={handleSearch}
            disabled={busy}
          >
            Search
          </button>
          <button
            className="rounded-lg bg-slate-700 px-3 py-2 text-sm font-semibold text-white transition hover:bg-slate-600 disabled:opacity-60"
            onClick={loadRecent}
            disabled={busy}
          >
            Recent
          </button>
        </div>
      </div>
      <div className="mt-4 space-y-3">
        {history.map((entry, index) => (
          <div key={`${entry.id || index}-${index}`} className="rounded-lg border border-slate-800 bg-slate-950/70 p-3">
            <div className="flex items-center justify-between text-xs text-slate-400">
              <span className="rounded-full bg-purple-800/60 px-2 py-1 text-purple-100 capitalize">
                {entry.kind}
              </span>
              <span className="truncate">{entry.id || entry.query}</span>
            </div>
            {entry.kind === "embed" && (
              <p className="mt-2 text-sm text-slate-100">Vector saved: {entry.saved || "(inline)"}</p>
            )}
            {entry.kind === "search" && (
              <div className="mt-2 space-y-2">
                {(entry.matches || []).map((m) => (
                  <div key={m.id} className="rounded border border-slate-800/70 bg-slate-900/60 p-2">
                    <div className="flex items-center justify-between text-xs text-slate-400">
                      <span>{m.id}</span>
                      <span className="text-emerald-300">{m.score?.toFixed(3)}</span>
                    </div>
                    <p className="mt-1 text-sm text-slate-100 whitespace-pre-wrap">{m.text}</p>
                  </div>
                ))}
                {!entry.matches?.length && <p className="text-sm text-slate-500">No matches.</p>}
              </div>
            )}
          </div>
        ))}
        {!history.length && <p className="text-sm text-slate-500">No vector actions yet.</p>}
      </div>

      <div className="mt-6">
        <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-400">Recent Vectors</h3>
        <div className="mt-2 space-y-2">
          {recent.map((m, idx) => (
            <div key={idx} className="rounded border border-slate-800/70 bg-slate-900/60 p-2">
              <div className="flex items-center justify-between text-xs text-slate-400">
                <span>{m.id || m.entry_id || "vector"}</span>
                <span className="text-emerald-300">{m.dimension ? `${m.dimension}d` : ""}</span>
              </div>
              <p className="mt-1 text-sm text-slate-100 whitespace-pre-wrap">
                {m.text ? `${m.text.slice(0, 240)}${m.text.length > 240 ? "..." : ""}` : "(no text)"}
              </p>
            </div>
          ))}
          {!recent.length && <p className="text-sm text-slate-500">Load recent vectors to view.</p>}
        </div>
      </div>
    </div>
  );
}
