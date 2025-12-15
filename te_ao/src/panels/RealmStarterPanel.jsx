import { useState } from "react";
import { useApi } from "../hooks/useApi.js";

export default function RealmStarterPanel() {
  const { request } = useApi();
  const [realmName, setRealmName] = useState("");
  const [description, setDescription] = useState("");
  const [template, setTemplate] = useState("basic");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [createdRealms, setCreatedRealms] = useState([]);

  const templates = [
    {
      id: "basic",
      name: "Basic Realm",
      description: "Minimal realm with core components",
    },
    {
      id: "with-kaitiaki",
      name: "With Kaitiaki",
      description: "Includes governance and guardian roles",
    },
    {
      id: "with-storage",
      name: "With Storage",
      description: "Includes document storage and indexing",
    },
    {
      id: "full",
      name: "Full Stack",
      description: "All features enabled",
    },
  ];

  const createRealm = async (e) => {
    e.preventDefault();
    if (!realmName.trim()) {
      setError("Realm name is required");
      return;
    }

    setLoading(true);
    setError("");
    setSuccess("");

    try {
      const response = await request("/api/realms/create", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: realmName,
          description,
          template,
          timestamp: new Date().toISOString(),
        }),
      });

      setSuccess(`✓ Realm "${realmName}" created successfully`);
      setCreatedRealms((prev) => [response, ...prev]);
      setRealmName("");
      setDescription("");
      setTemplate("basic");

      setTimeout(() => setSuccess(""), 3000);
    } catch (err) {
      setError(`Failed to create realm: ${String(err)}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full h-screen flex flex-col bg-slate-950 text-slate-100">
      {/* Header */}
      <div className="border-b border-slate-700 bg-slate-900 p-4">
        <h1 className="text-2xl font-bold text-cyan-400">Realm Starter</h1>
        <p className="text-sm text-slate-400">Create new realms from templates via te_hau</p>
      </div>

      {/* Main content */}
      <div className="flex-1 flex gap-4 overflow-hidden p-4">
        {/* Form Panel */}
        <div className="w-96 flex flex-col bg-slate-900 rounded border border-slate-700 overflow-hidden">
          <div className="border-b border-slate-700 bg-slate-800 px-4 py-3">
            <h2 className="font-bold text-cyan-400">Create New Realm</h2>
          </div>
          <div className="flex-1 overflow-y-auto p-4">
            <form onSubmit={createRealm} className="space-y-4">
              {/* Realm Name */}
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">
                  Realm Name
                </label>
                <input
                  type="text"
                  value={realmName}
                  onChange={(e) => setRealmName(e.target.value)}
                  placeholder="e.g., te_wai, te_ahi"
                  className="w-full px-3 py-2 bg-slate-800 border border-slate-600 rounded text-sm font-mono focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500"
                  disabled={loading}
                />
              </div>

              {/* Description */}
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">
                  Description
                </label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="What is this realm for?"
                  rows="3"
                  className="w-full px-3 py-2 bg-slate-800 border border-slate-600 rounded text-sm font-mono focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500"
                  disabled={loading}
                />
              </div>

              {/* Template Selection */}
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Template
                </label>
                <div className="space-y-2">
                  {templates.map((t) => (
                    <label
                      key={t.id}
                      className="flex items-center p-2 border rounded cursor-pointer hover:bg-slate-800 transition"
                      style={{
                        borderColor: template === t.id ? "#06b6d4" : "#475569",
                        backgroundColor: template === t.id ? "#0f172a" : "transparent",
                      }}
                    >
                      <input
                        type="radio"
                        name="template"
                        value={t.id}
                        checked={template === t.id}
                        onChange={(e) => setTemplate(e.target.value)}
                        disabled={loading}
                        className="mr-2"
                      />
                      <div>
                        <div className="text-sm font-medium">{t.name}</div>
                        <div className="text-xs text-slate-400">{t.description}</div>
                      </div>
                    </label>
                  ))}
                </div>
              </div>

              {/* Messages */}
              {error && (
                <div className="p-2 bg-red-950 border border-red-700 rounded text-sm text-red-300">
                  {error}
                </div>
              )}
              {success && (
                <div className="p-2 bg-green-950 border border-green-700 rounded text-sm text-green-300">
                  {success}
                </div>
              )}

              {/* Submit Button */}
              <button
                type="submit"
                disabled={loading}
                className="w-full px-4 py-2 bg-cyan-600 hover:bg-cyan-700 disabled:bg-slate-600 rounded font-medium transition"
              >
                {loading ? "Creating..." : "Create Realm"}
              </button>
            </form>
          </div>
        </div>

        {/* History Panel */}
        <div className="flex-1 flex flex-col bg-slate-900 rounded border border-slate-700 overflow-hidden">
          <div className="border-b border-slate-700 bg-slate-800 px-4 py-3">
            <h2 className="font-bold text-cyan-400">Created Realms</h2>
          </div>
          <div className="flex-1 overflow-y-auto p-4">
            {createdRealms.length > 0 ? (
              <div className="space-y-3">
                {createdRealms.map((realm, idx) => (
                  <div
                    key={idx}
                    className="border border-slate-600 rounded p-3 bg-slate-800 hover:bg-slate-750 transition"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="font-bold text-cyan-300">{realm.name}</h3>
                      <span className="text-xs bg-cyan-900 text-cyan-200 px-2 py-1 rounded">
                        {realm.template}
                      </span>
                    </div>
                    {realm.description && (
                      <p className="text-sm text-slate-300 mb-2">{realm.description}</p>
                    )}
                    <div className="text-xs text-slate-400">
                      Created: {new Date(realm.timestamp).toLocaleString()}
                    </div>
                    {realm.path && (
                      <div className="text-xs font-mono text-slate-500 mt-1">
                        Path: {realm.path}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-slate-400">
                <p className="text-sm">No realms created yet</p>
                <p className="text-xs text-slate-500 mt-1">Create one using the form →</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
