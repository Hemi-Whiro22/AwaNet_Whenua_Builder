import { useCallback, useState } from "react";
import { useApi } from "../hooks/useApi.js";

export default function OCRPanel() {
  const { request } = useApi();
  const [file, setFile] = useState(null);
  const [history, setHistory] = useState([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const onDrop = useCallback((event) => {
    event.preventDefault();
    const picked = event.dataTransfer.files?.[0];
    if (picked) setFile(picked);
  }, []);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    if (!file) {
      setError("Select or drop an image first.");
      return;
    }
    const formData = new FormData();
    formData.append("file", file);
    setBusy(true);
    try {
      const result = await request("/intake/ocr", { method: "POST", body: formData });
      setHistory((prev) => [result, ...prev].slice(0, 10));
    } catch (err) {
      setError(err.message || "Upload failed.");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-6 shadow-lg shadow-black/30">
      <h2 className="text-xl font-semibold text-emerald-200">OCR</h2>
      <p className="mt-2 text-sm text-slate-300">
        Drop or select an image. Backend: /intake/ocr → gpt-4o-mini-vision.
      </p>
      <form onSubmit={handleSubmit} className="mt-4 flex flex-col gap-3">
        <div
          className="rounded-xl border-2 border-dashed border-slate-700 bg-slate-950/40 p-4 text-center text-sm text-slate-200 cursor-pointer"
          onDrop={onDrop}
          onDragOver={(e) => e.preventDefault()}
          onClick={() => document.getElementById("ocr-file").click()}
        >
          {file ? file.name : "Drag an image here or click to choose"}
        </div>
        <input
          id="ocr-file"
          type="file"
          accept="image/*"
          className="hidden"
          onChange={(event) => setFile(event.target.files?.[0] ?? null)}
        />
        <button
          className="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-emerald-500 disabled:opacity-60"
          type="submit"
          disabled={busy}
        >
          {busy ? "Processing..." : "Extract Text"}
        </button>
        {error && <p className="text-sm text-rose-300">{error}</p>}
      </form>
      <div className="mt-4 space-y-3">
        {history.map((entry) => (
          <div key={entry.id} className="rounded-lg border border-slate-800 bg-slate-950/70 p-3">
            <div className="flex items-center justify-between text-xs text-slate-400">
              <span className="rounded-full bg-emerald-800/60 px-2 py-1 text-emerald-200">OCR</span>
              <span className="truncate">{entry.id}</span>
            </div>
            <p className="mt-2 text-sm text-slate-100 whitespace-pre-wrap">
              {entry.text || "(no text returned)"}
            </p>
            {entry.saved && <p className="mt-1 text-xs text-slate-500">saved: {entry.saved}</p>}
          </div>
        ))}
        {!history.length && <p className="text-sm text-slate-500">No OCR runs yet.</p>}
      </div>
    </div>
  );
}
