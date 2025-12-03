import { useEffect, useState, useMemo } from "react";
import { useApi } from "../hooks/useApi.js";

const Spinner = () => (
  <div className="flex items-center gap-2 text-sm text-emerald-300">
    <span className="h-4 w-4 animate-spin rounded-full border-2 border-emerald-400 border-t-transparent" />
    <span>Thinking...</span>
  </div>
);

export default function ChatPanel() {
  const { request, baseUrl } = useApi();
  const callApi = useMemo(() => request, [request]); // helper alias

  const [logs, setLogs] = useState([]);
  const [prompt, setPrompt] = useState("");
  const [history, setHistory] = useState([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    let mounted = true;
    const loadLogs = async () => {
      try {
        const data = await request("/memory"); // placeholder endpoint
        if (!mounted) return;
        setLogs(Array.isArray(data) ? data.slice(0, 10) : []);
      } catch {
        if (!mounted) setLogs([]);
      }
    };
    loadLogs();
    return () => {
      mounted = false;
    };
  }, [request]);

  const onSubmit = async (event) => {
    event.preventDefault();
    setError("");
    if (!prompt.trim()) {
      setError("Type something to send.");
      return;
    }
    setBusy(true);
    try {
      const payload = { text: prompt, source: "ui-chat" };
      const reply = await callApi("/assistant/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      setHistory((prev) => [{ prompt, reply }, ...prev].slice(0, 10));
      setPrompt("");
    } catch (err) {
      setError(err.message || "Assistant call failed.");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-6 shadow-lg shadow-black/30">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold text-emerald-200">Assistant Chat</h2>
        <span className="text-xs text-slate-400">API: {baseUrl}</span>
      </div>
      <p className="mt-2 text-sm text-slate-300">
        Send prompts to the assistant (tool-calls available) and view recent pipeline runs.
      </p>

      <form onSubmit={onSubmit} className="mt-4 flex flex-col gap-3">
        <textarea
          className="min-h-[120px] w-full rounded-lg border border-slate-800 bg-slate-950/60 p-3 text-slate-100"
          placeholder="Ask Kitenga Whiro…"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          disabled={busy}
        />
        <div className="flex items-center gap-3">
          <button
            type="submit"
            className="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-emerald-500 disabled:opacity-60"
            disabled={busy}
          >
            {busy ? "Sending..." : "Send"}
          </button>
          {busy && <Spinner />}
          {error && <p className="text-sm text-rose-300">{error}</p>}
        </div>
      </form>

      <div className="mt-6">
        <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-400">Conversation</h3>
        <div className="mt-2 space-y-3">
          {history.map((item, idx) => (
            <div key={idx} className="rounded-xl border border-slate-800 bg-slate-950/70 p-4">
              <p className="text-xs text-slate-400">You</p>
              <p className="mt-1 text-sm text-slate-100 whitespace-pre-wrap">{item.prompt}</p>
              <p className="mt-3 text-xs text-emerald-300">Assistant</p>
              <p className="mt-1 text-sm text-emerald-100 whitespace-pre-wrap">
                {item.reply?.output || item.reply?.summary || item.reply?.clean_file || "(no reply content)"}
              </p>
              <div className="mt-2 text-xs text-slate-500 flex flex-wrap gap-3">
                {item.reply?.source && <span>source: {item.reply.source}</span>}
                {item.reply?.clean_file && <span>clean: {item.reply.clean_file}</span>}
                {item.reply?.raw_file && <span>raw: {item.reply.raw_file}</span>}
                {item.reply?.chunk_count != null && <span>chunks: {item.reply.chunk_count}</span>}
              </div>
            </div>
          ))}
          {!history.length && <p className="text-sm text-slate-500">No prompts sent yet.</p>}
        </div>
      </div>

      <div className="mt-6">
        <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-400">Recent Pipeline Logs</h3>
        <div className="mt-2 space-y-3">
          {logs.slice(0, 10).map((entry, idx) => (
            <div key={`${entry.id}-${idx}`} className="rounded-xl border border-slate-800 bg-slate-950/60 p-3">
              <div className="flex items-center justify-between text-xs text-slate-400">
                <span className="rounded-full bg-slate-800 px-2 py-1 text-slate-100">
                  {entry.source || "pipeline"}
                </span>
                <span>{entry.created_at || entry.ts || "—"}</span>
              </div>
              <p className="mt-2 text-sm text-slate-100">{entry.content || entry.text || "(no content)"}</p>
              {entry.raw_file && <p className="mt-1 text-xs text-slate-500">raw: {entry.raw_file}</p>}
              {entry.clean_file && <p className="mt-1 text-xs text-slate-500">clean: {entry.clean_file}</p>}
            </div>
          ))}
          {!logs.length && <p className="text-sm text-slate-500">No logs found.</p>}
        </div>
      </div>
    </div>
  );
}
