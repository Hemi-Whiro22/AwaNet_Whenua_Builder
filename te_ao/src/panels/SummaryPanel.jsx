import { useState } from "react";
import { useApi } from "../hooks/useApi.js";

export default function SummaryPanel() {
  const { request } = useApi();
  const [text, setText] = useState("");
  const [mode, setMode] = useState("research");
  const [busy, setBusy] = useState(false);
  const [history, setHistory] = useState([]);
  const [error, setError] = useState("");

  const handleFile = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;
    const content = await file.text();
    setText(content);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    if (!text.trim()) {
      setError("Add some text first.");
      return;
    }
    setBusy(true);
    try {
      const result = await request("/intake/summarize", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text, mode }),
      });
      setHistory((prev) => [result, ...prev].slice(0, 10));
    } catch (err) {
      setError(err.message || "Summary failed.");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-6 shadow-lg shadow-black/30">
      <h2 className="text-xl font-semibold text-emerald-200">Summary</h2>
      <p className="mt-2 text-sm text-slate-300">
        Text → /intake/summarize with research or taonga tone.
      </p>
      <form onSubmit={handleSubmit} className="mt-4 flex flex-col gap-3">
        <textarea
          className="min-h-[140px] w-full rounded-lg border border-slate-800 bg-slate-950/60 p-3 text-slate-100"
          placeholder="Paste text or drop a file..."
          value={text}
          onChange={(event) => setText(event.target.value)}
        />
        <div className="flex items-center gap-3 text-sm text-slate-200">
          <label className="flex items-center gap-2">
            <input
              type="radio"
              name="mode"
              value="research"
              checked={mode === "research"}
              onChange={() => setMode("research")}
            />
            Research
          </label>
          <label className="flex items-center gap-2">
            <input
              type="radio"
              name="mode"
              value="taonga"
              checked={mode === "taonga"}
              onChange={() => setMode("taonga")}
            />
            Taonga
          </label>
          <label className="ml-auto cursor-pointer text-emerald-300 underline">
            <input type="file" accept=".txt,.md,.json,.yaml,.yml" className="hidden" onChange={handleFile} />
            Load file
          </label>
        </div>
        <button
          className="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-emerald-500 disabled:opacity-60"
          type="submit"
          disabled={busy}
        >
          {busy ? "Summarising..." : "Summarise"}
        </button>
        {error && <p className="text-sm text-rose-300">{error}</p>}
      </form>
      <div className="mt-4 space-y-3">
        {history.map((entry) => (
          <div key={entry.id} className="rounded-lg border border-slate-800 bg-slate-950/70 p-3">
            <div className="flex items-center justify-between text-xs text-slate-400">
              <span className="rounded-full bg-blue-800/60 px-2 py-1 text-blue-100">Summary ({entry.mode})</span>
              <span className="truncate">{entry.id}</span>
            </div>
            <p className="mt-2 whitespace-pre-wrap text-sm text-slate-100">{entry.summary || "(empty)"} </p>
          </div>
        ))}
        {!history.length && <p className="text-sm text-slate-500">No summaries yet.</p>}
      </div>
    </div>
  );
}
