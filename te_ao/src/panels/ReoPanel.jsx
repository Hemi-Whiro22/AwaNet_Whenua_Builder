import { useState } from "react";
import { useApi } from "../hooks/useApi.js";

export default function ReoPanel() {
  const { request } = useApi();
  const [text, setText] = useState("");
  const [history, setHistory] = useState([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const run = async (kind, path) => {
    setError("");
    if (!text.trim()) {
      setError("Add some text first.");
      return;
    }
    setBusy(true);
    try {
      const result = await request(path, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      });
      setHistory((prev) => [{ ...result, kind }, ...prev].slice(0, 10));
    } catch (err) {
      setError(err.message || "Request failed.");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-6 shadow-lg shadow-black/30">
      <h2 className="text-xl font-semibold text-emerald-200">Reo Tools</h2>
      <p className="mt-2 text-sm text-slate-300">Translate, explain, or pronounce with Māori-safe prompts.</p>
      <div className="mt-4 flex flex-col gap-3">
        <textarea
          className="min-h-[120px] w-full rounded-lg border border-slate-800 bg-slate-950/60 p-3 text-slate-100"
          placeholder="Type kupu here..."
          value={text}
          onChange={(event) => setText(event.target.value)}
        />
        <div className="flex flex-wrap gap-2">
          <button
            className="rounded-lg bg-emerald-600 px-3 py-2 text-sm font-semibold text-white transition hover:bg-emerald-500 disabled:opacity-60"
            onClick={() => run("translate", "/reo/translate")}
            disabled={busy}
          >
            Translate
          </button>
          <button
            className="rounded-lg bg-blue-600 px-3 py-2 text-sm font-semibold text-white transition hover:bg-blue-500 disabled:opacity-60"
            onClick={() => run("explain", "/reo/explain")}
            disabled={busy}
          >
            Explain
          </button>
          <button
            className="rounded-lg bg-amber-600 px-3 py-2 text-sm font-semibold text-white transition hover:bg-amber-500 disabled:opacity-60"
            onClick={() => run("pronounce", "/reo/pronounce")}
            disabled={busy}
          >
            Pronounce
          </button>
        </div>
        {error && <p className="text-sm text-rose-300">{error}</p>}
      </div>
      <div className="mt-4 space-y-3">
        {history.map((entry, index) => (
          <div key={`${entry.id}-${index}`} className="rounded-lg border border-slate-800 bg-slate-950/70 p-3">
            <div className="flex items-center justify-between text-xs text-slate-400">
              <span className="rounded-full bg-slate-800 px-2 py-1 text-slate-100 capitalize">{entry.kind}</span>
              <span className="truncate">{entry.id}</span>
            </div>
            <p className="mt-2 whitespace-pre-wrap text-sm text-slate-100">
              {entry.output || entry.error || "(no output)"}
            </p>
          </div>
        ))}
        {!history.length && <p className="text-sm text-slate-500">No reo calls yet.</p>}
      </div>
    </div>
  );
}
