
import { useEffect, useState } from "react";
import { useApi } from "../hooks/useApi";

const DEFAULT_MODEL = "gpt-4o";

export default function KaitiakiBuilderPanel() {
  const { request } = useApi();
  const [kaitiaki, setKaitiaki] = useState([]);
  const [name, setName] = useState("");
  const [role, setRole] = useState("");
  const [model, setModel] = useState(DEFAULT_MODEL);
  const [notes, setNotes] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const load = async () => {
    try {
      const data = await request("/kaitiaki");
      setKaitiaki(data || []);
    } catch (err) {
      setError(err.message || "Unable to load kaitiaki");
    }
  };

  useEffect(() => {
    load();
  }, []);

  const handleCreate = async (event) => {
    event.preventDefault();
    setError("");
    setMessage("");
    if (!name.trim()) {
      setError("Name is required");
      return;
    }
    setBusy(true);
    try {
      const payload = {
        name: name.trim(),
        role: role.trim(),
        models: { primary: model || DEFAULT_MODEL },
        notes: notes.trim(),
      };
      const res = await request("/kaitiaki", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      setMessage(`Saved ${res.slug}`);
      setName("");
      setRole("");
      setNotes("");
      setModel(DEFAULT_MODEL);
      await load();
    } catch (err) {
      setError(err.message || "Create failed");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-6 shadow-lg shadow-black/30">
        <h2 className="text-xl font-semibold text-emerald-200">Kaitiaki Builder</h2>
        <p className="mt-2 text-sm text-slate-300">Create or inspect kaitiaki definitions stored in mauri/kaitiaki.</p>
        <form onSubmit={handleCreate} className="mt-4 grid gap-3 md:grid-cols-2">
          <label className="flex flex-col gap-1 text-sm text-slate-200">
            Name
            <input
              className="rounded-lg border border-slate-800 bg-slate-950/60 px-3 py-2 text-slate-100"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g., Te Kitenga Nui"
            />
          </label>
          <label className="flex flex-col gap-1 text-sm text-slate-200">
            Primary model
            <input
              className="rounded-lg border border-slate-800 bg-slate-950/60 px-3 py-2 text-slate-100"
              value={model}
              onChange={(e) => setModel(e.target.value)}
              placeholder="gpt-4o"
            />
          </label>
          <label className="md:col-span-2 flex flex-col gap-1 text-sm text-slate-200">
            Role / purpose
            <input
              className="rounded-lg border border-slate-800 bg-slate-950/60 px-3 py-2 text-slate-100"
              value={role}
              onChange={(e) => setRole(e.target.value)}
              placeholder="Dev-facing UI persona for Kitenga Whiro"
            />
          </label>
          <label className="md:col-span-2 flex flex-col gap-1 text-sm text-slate-200">
            Notes
            <textarea
              className="rounded-lg border border-slate-800 bg-slate-950/60 px-3 py-2 text-slate-100 min-h-[80px]"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Capabilities, constraints, links..."
            />
          </label>
          <div className="md:col-span-2 flex items-center gap-3">
            <button
              type="submit"
              className="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-emerald-500 disabled:opacity-60"
              disabled={busy}
            >
              {busy ? "Saving..." : "Save Kaitiaki"}
            </button>
            {error && <span className="text-sm text-rose-300">{error}</span>}
            {message && <span className="text-sm text-emerald-300">{message}</span>}
          </div>
        </form>
      </div>

      <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-6 shadow-lg shadow-black/30">
        <h3 className="text-lg font-semibold text-slate-100">Existing</h3>
        <div className="mt-3 grid gap-3 md:grid-cols-2">
          {kaitiaki.map((k) => (
            <div key={k.id || k.name} className="rounded-xl border border-slate-800 bg-slate-950/70 p-4">
              <div className="flex items-center justify-between text-xs text-slate-400">
                <span className="rounded-full bg-slate-800 px-2 py-1 text-slate-100">{k.realm || "te_ao"}</span>
                <span className="truncate">{k.models?.primary || model}</span>
              </div>
              <div className="mt-2 text-base font-semibold text-white">{k.name}</div>
              <p className="text-sm text-slate-300">{k.role || "(no role)"}</p>
              {k.notes && <p className="mt-2 text-xs text-slate-400 whitespace-pre-wrap">{k.notes}</p>}
            </div>
          ))}
        </div>
        {!kaitiaki.length && <p className="text-sm text-slate-500">No kaitiaki saved yet.</p>}
      </div>
    </div>
  );
}
