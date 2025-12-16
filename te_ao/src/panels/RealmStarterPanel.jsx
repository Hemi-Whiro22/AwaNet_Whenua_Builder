import { useState, useEffect } from "react";
import { useApi } from "../hooks/useApi.js";

const Spinner = ({ text = "Loading..." }) => (
  <div className="flex items-center gap-2 text-sm text-cyan-400">
    <span className="h-3 w-3 animate-spin rounded-full border-2 border-cyan-400 border-t-transparent" />
    <span>{text}</span>
  </div>
);

export default function RealmStarterPanel() {
  const { request, baseUrl } = useApi();
  
  // Form state
  const [realmName, setRealmName] = useState("");
  const [description, setDescription] = useState("");
  const [kaitiakiName, setKaitiakiName] = useState("");
  const [kaitiakiRole, setKaitiakiRole] = useState("");
  const [kaitiakiInstructions, setKaitiakiInstructions] = useState("");
  
  // Template selection
  const [template, setTemplate] = useState("full");
  
  // API selection for realm
  const [selectedApis, setSelectedApis] = useState([
    "vector", "memory", "intake", "assistant"
  ]);
  
  // Loading/status
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  
  // Created realms
  const [createdRealms, setCreatedRealms] = useState([]);
  
  // Available APIs to include in realm
  const availableApis = [
    { id: "vector", name: "Vector Search", desc: "Semantic search via OpenAI embeddings" },
    { id: "memory", name: "Memory/Context", desc: "Supabase memory table for context" },
    { id: "intake", name: "Intake Pipeline", desc: "Document ingestion and processing" },
    { id: "assistant", name: "OpenAI Assistant", desc: "Dedicated assistant + vector store" },
    { id: "ocr", name: "OCR Pipeline", desc: "Image/PDF text extraction" },
    { id: "translation", name: "Te Reo Translation", desc: "Māori language support" },
    { id: "research", name: "Web Research", desc: "Web search integration" },
    { id: "chat", name: "Chat API", desc: "Conversational endpoints" },
  ];

  const templates = [
    { id: "basic", name: "Basic Realm", desc: "Minimal - just proxy + state", apis: ["memory"] },
    { id: "with-kaitiaki", name: "With Kaitiaki", desc: "Guardian with assistant", apis: ["memory", "assistant", "chat"] },
    { id: "with-storage", name: "With Storage", desc: "Document storage + search", apis: ["memory", "vector", "intake"] },
    { id: "full", name: "Full Stack", desc: "All features enabled", apis: availableApis.map(a => a.id) },
  ];

  // Update selected APIs when template changes
  useEffect(() => {
    const tpl = templates.find(t => t.id === template);
    if (tpl) {
      setSelectedApis(tpl.apis);
    }
  }, [template]);

  // Load existing realms on mount
  useEffect(() => {
    loadExistingRealms();
  }, []);

  const loadExistingRealms = async () => {
    try {
      const res = await request("/realms/list");
      if (res.success && res.data?.realms) {
        setCreatedRealms(res.data.realms.map(r => ({
          name: r.config?.realm_name || r.path?.split('/').pop(),
          kaitiaki: r.config?.kaitiaki,
          realm_path: r.path,
          assistant_id: r.config?.openai?.assistant_id,
          vector_store_id: r.config?.openai?.vector_store_id,
          urls: r.config?.urls,
          created_at: r.config?.created_at,
          apis: r.config?.apis || []
        })));
      }
    } catch (err) {
      console.log("Could not load existing realms:", err);
    }
  };

  const toggleApi = (apiId) => {
    setSelectedApis(prev => 
      prev.includes(apiId) 
        ? prev.filter(id => id !== apiId)
        : [...prev, apiId]
    );
    // Switch to custom when manually toggling
    setTemplate("custom");
  };

  const createRealm = async (e) => {
    e.preventDefault();
    if (!realmName.trim()) {
      setError("Realm name is required");
      return;
    }
    if (!kaitiakiName.trim()) {
      setError("Kaitiaki name is required");
      return;
    }

    setLoading(true);
    setError("");
    setSuccess("");

    try {
      const res = await request("/realms/create", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          realm_name: realmName,
          kaitiaki_name: kaitiakiName,
          description: `${description || ''}${kaitiakiRole ? ` Role: ${kaitiakiRole}` : ''}`.trim() || `Realm for ${kaitiakiName}`,
          apis: selectedApis,
          template: template,
        }),
      });

      if (res.success) {
        const config = res.data?.config || {};
        setSuccess(`✓ Realm "${realmName}" created at ${res.data?.realm_path}`);
        
        setCreatedRealms(prev => [{
          name: realmName,
          kaitiaki: kaitiakiName,
          realm_path: res.data?.realm_path,
          assistant_id: config.openai?.assistant_id,
          vector_store_id: config.openai?.vector_store_id,
          urls: config.urls,
          created_at: config.created_at || new Date().toISOString(),
          apis: selectedApis
        }, ...prev]);

        // Clear form
        setRealmName("");
        setDescription("");
        setKaitiakiName("");
        setKaitiakiRole("");
        setKaitiakiInstructions("");
        setTemplate("full");
        
        setTimeout(() => setSuccess(""), 5000);
      } else {
        setError(res.message || "Failed to create realm");
      }
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
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-cyan-400">🏰 Realm Starter</h1>
            <p className="text-sm text-slate-400">Create new realms with devcontainer, kaitiaki, and OpenAI assistant</p>
          </div>
          <span className="text-xs text-slate-500">{baseUrl}</span>
        </div>
        {error && <p className="text-red-400 text-sm mt-2 bg-red-950 border border-red-700 rounded px-3 py-1">{error}</p>}
        {success && <p className="text-green-400 text-sm mt-2 bg-green-950 border border-green-700 rounded px-3 py-1">{success}</p>}
      </div>

      {/* Main content */}
      <div className="flex-1 flex gap-4 overflow-hidden p-4">
        {/* Form Panel */}
        <div className="w-[450px] flex flex-col bg-slate-900 rounded border border-slate-700 overflow-hidden">
          <div className="border-b border-slate-700 bg-slate-800 px-4 py-3">
            <h2 className="font-bold text-cyan-400">Create New Realm</h2>
          </div>
          <div className="flex-1 overflow-y-auto p-4">
            <form onSubmit={createRealm} className="space-y-4">
              {/* Realm Name */}
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">
                  Realm Name *
                </label>
                <input
                  type="text"
                  value={realmName}
                  onChange={(e) => setRealmName(e.target.value)}
                  placeholder="e.g., te_wai, te_ahi"
                  className="w-full px-3 py-2 bg-slate-800 border border-slate-600 rounded text-sm focus:outline-none focus:border-cyan-500"
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
                  rows="2"
                  className="w-full px-3 py-2 bg-slate-800 border border-slate-600 rounded text-sm focus:outline-none focus:border-cyan-500"
                  disabled={loading}
                />
              </div>

              {/* Kaitiaki Section */}
              <div className="border border-cyan-800 rounded p-3 bg-cyan-950/30">
                <p className="text-xs text-cyan-400 font-medium mb-2">🛡️ Kaitiaki (Guardian)</p>
                <div className="space-y-2">
                  <input
                    type="text"
                    value={kaitiakiName}
                    onChange={(e) => setKaitiakiName(e.target.value)}
                    placeholder="Kaitiaki Name *"
                    className="w-full px-3 py-2 bg-slate-800 border border-slate-600 rounded text-sm focus:outline-none focus:border-cyan-500"
                    disabled={loading}
                  />
                  <input
                    type="text"
                    value={kaitiakiRole}
                    onChange={(e) => setKaitiakiRole(e.target.value)}
                    placeholder="Role (e.g., Guardian of Water)"
                    className="w-full px-3 py-2 bg-slate-800 border border-slate-600 rounded text-sm focus:outline-none focus:border-cyan-500"
                    disabled={loading}
                  />
                  <textarea
                    value={kaitiakiInstructions}
                    onChange={(e) => setKaitiakiInstructions(e.target.value)}
                    placeholder="System instructions for assistant (optional)"
                    rows="2"
                    className="w-full px-3 py-2 bg-slate-800 border border-slate-600 rounded text-sm focus:outline-none focus:border-cyan-500"
                    disabled={loading}
                  />
                </div>
              </div>

              {/* Template Selection */}
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Template
                </label>
                <div className="grid grid-cols-2 gap-2">
                  {templates.map((t) => (
                    <button
                      key={t.id}
                      type="button"
                      onClick={() => setTemplate(t.id)}
                      disabled={loading}
                      className={`p-2 border rounded text-left transition ${
                        template === t.id
                          ? "border-cyan-500 bg-cyan-950"
                          : "border-slate-600 bg-slate-800 hover:bg-slate-750"
                      }`}
                    >
                      <div className="text-sm font-medium">{t.name}</div>
                      <div className="text-xs text-slate-400">{t.desc}</div>
                    </button>
                  ))}
                </div>
              </div>

              {/* API Selection */}
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  APIs to Include
                </label>
                <div className="grid grid-cols-2 gap-2 max-h-48 overflow-y-auto">
                  {availableApis.map((api) => (
                    <label
                      key={api.id}
                      className={`flex items-start p-2 border rounded cursor-pointer transition ${
                        selectedApis.includes(api.id)
                          ? "border-emerald-500 bg-emerald-950/50"
                          : "border-slate-600 bg-slate-800 hover:bg-slate-750"
                      }`}
                    >
                      <input
                        type="checkbox"
                        checked={selectedApis.includes(api.id)}
                        onChange={() => toggleApi(api.id)}
                        disabled={loading}
                        className="mr-2 mt-1"
                      />
                      <div>
                        <div className="text-xs font-medium">{api.name}</div>
                        <div className="text-[10px] text-slate-400">{api.desc}</div>
                      </div>
                    </label>
                  ))}
                </div>
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={loading}
                className="w-full px-4 py-3 bg-cyan-600 hover:bg-cyan-700 disabled:bg-slate-600 rounded font-medium transition flex items-center justify-center gap-2"
              >
                {loading ? (
                  <Spinner text="Creating realm..." />
                ) : (
                  <>🏰 Create Realm + Assistant + Vector Store</>
                )}
              </button>
              
              <p className="text-xs text-slate-500 text-center">
                Creates: OpenAI Assistant, Vector Store, Devcontainer, Full project scaffold
              </p>
            </form>
          </div>
        </div>

        {/* Created Realms Panel */}
        <div className="flex-1 flex flex-col bg-slate-900 rounded border border-slate-700 overflow-hidden">
          <div className="border-b border-slate-700 bg-slate-800 px-4 py-3 flex justify-between items-center">
            <h2 className="font-bold text-cyan-400">Created Realms ({createdRealms.length})</h2>
            <button
              onClick={loadExistingRealms}
              className="text-xs text-slate-400 hover:text-slate-200"
            >
              Refresh
            </button>
          </div>
          <div className="flex-1 overflow-y-auto p-4">
            {createdRealms.length > 0 ? (
              <div className="space-y-3">
                {createdRealms.map((realm, idx) => (
                  <div
                    key={idx}
                    className="border border-cyan-800 rounded p-3 bg-cyan-950/30"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div>
                        <h3 className="font-bold text-cyan-300 text-lg">🏰 {realm.name}</h3>
                        {realm.kaitiaki && (
                          <p className="text-sm text-emerald-400">🛡️ {realm.kaitiaki}</p>
                        )}
                      </div>
                      <span className="text-[10px] text-slate-500">
                        {realm.created_at ? new Date(realm.created_at).toLocaleDateString() : ''}
                      </span>
                    </div>
                    
                    {realm.realm_path && (
                      <div className="bg-slate-800 rounded p-2 mb-2">
                        <p className="text-[10px] text-slate-400 mb-1">📁 Path:</p>
                        <p className="text-orange-400 font-mono text-xs">{realm.realm_path}</p>
                      </div>
                    )}
                    
                    {(realm.assistant_id || realm.vector_store_id) && (
                      <div className="bg-slate-800 rounded p-2 mb-2">
                        <p className="text-[10px] text-slate-400 mb-1">🤖 OpenAI:</p>
                        {realm.assistant_id && (
                          <p className="text-purple-400 font-mono text-[10px]">Assistant: {realm.assistant_id}</p>
                        )}
                        {realm.vector_store_id && (
                          <p className="text-blue-400 font-mono text-[10px]">Vector: {realm.vector_store_id}</p>
                        )}
                      </div>
                    )}
                    
                    {realm.urls && (
                      <div className="bg-slate-800 rounded p-2 mb-2">
                        <p className="text-[10px] text-slate-400 mb-1">🔗 URLs:</p>
                        {realm.urls.cloudflare && <p className="text-sky-400 text-[10px]">☁️ {realm.urls.cloudflare}</p>}
                        {realm.urls.backend && <p className="text-green-400 text-[10px]">🖥️ {realm.urls.backend}</p>}
                      </div>
                    )}
                    
                    {realm.apis && realm.apis.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-2">
                        {realm.apis.map(api => (
                          <span key={api} className="text-[10px] bg-slate-700 text-slate-300 px-2 py-0.5 rounded">
                            {api}
                          </span>
                        ))}
                      </div>
                    )}
                    
                    <div className="mt-2 pt-2 border-t border-cyan-800">
                      <p className="text-slate-500 text-[10px]">💡 Open folder in VS Code → Reopen in Container</p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-slate-400">
                <p className="text-4xl mb-2">🏰</p>
                <p className="text-sm">No realms created yet</p>
                <p className="text-xs text-slate-500 mt-1">Create one using the form ←</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
