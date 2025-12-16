import { useState, useEffect } from "react";
import { useApi } from "../hooks/useApi.js";

/**
 * KitengaDevHub - Master dev panel for Kitenga Whiro
 * Features:
 * - Live vector recall across all vector stores
 * - Web search integration
 * - Document ingestion (PDF, MD, images)
 * - Realm generator with OpenAI assistant + vector store creation
 * - Kitenga schema database access
 */

const Spinner = ({ text = "Loading..." }) => (
  <div className="flex items-center gap-2 text-sm text-sky-400">
    <span className="h-3 w-3 animate-spin rounded-full border-2 border-sky-400 border-t-transparent" />
    <span>{text}</span>
  </div>
);

export default function KitengaDevHub() {
  const { request, baseUrl } = useApi();
  const [activeSection, setActiveSection] = useState("vector");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [results, setResults] = useState(null);

  // Vector Search state
  const [vectorQuery, setVectorQuery] = useState("");
  const [topK, setTopK] = useState(5);
  const [vectorResults, setVectorResults] = useState([]);

  // Web Search state
  const [webQuery, setWebQuery] = useState("");
  const [webResults, setWebResults] = useState([]);

  // Ingestion state
  const [file, setFile] = useState(null);
  const [ingestText, setIngestText] = useState("");
  const [ingestType, setIngestType] = useState("text");
  const [ingestResults, setIngestResults] = useState([]);

  // Realm Generator state
  const [realmName, setRealmName] = useState("");
  const [realmDescription, setRealmDescription] = useState("");
  const [kaitiakiName, setKaitiakiName] = useState("");
  const [kaitiakiRole, setKaitiakiRole] = useState("");
  const [kaitiakiInstructions, setKaitiakiInstructions] = useState("");
  const [createdRealms, setCreatedRealms] = useState([]);

  // Database state
  const [dbStats, setDbStats] = useState(null);
  const [dbLogs, setDbLogs] = useState([]);

  // ==================== VECTOR SEARCH ====================
  const handleVectorSearch = async () => {
    if (!vectorQuery.trim()) return;
    setLoading(true);
    setError("");
    try {
      const res = await request("/vector/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: vectorQuery, top_k: topK, rerank: true }),
      });
      setVectorResults(res.matches || res.results || []);
    } catch (err) {
      setError(String(err));
    } finally {
      setLoading(false);
    }
  };

  const handleVectorEmbed = async () => {
    if (!vectorQuery.trim()) return;
    setLoading(true);
    setError("");
    try {
      const res = await request("/vector/embed", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: vectorQuery }),
      });
      setVectorResults([{ type: "embedded", ...res }]);
    } catch (err) {
      setError(String(err));
    } finally {
      setLoading(false);
    }
  };

  // ==================== WEB SEARCH ====================
  const handleWebSearch = async () => {
    if (!webQuery.trim()) return;
    setLoading(true);
    setError("");
    try {
      const res = await request("/research/web_search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: webQuery, num_results: 10 }),
      });
      setWebResults(res.results || res || []);
    } catch (err) {
      setError(String(err));
    } finally {
      setLoading(false);
    }
  };

  const handleStackedSearch = async () => {
    if (!webQuery.trim()) return;
    setLoading(true);
    setError("");
    try {
      const res = await request("/research/stacked", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: webQuery }),
      });
      setWebResults(res.results || [res]);
    } catch (err) {
      setError(String(err));
    } finally {
      setLoading(false);
    }
  };

  // ==================== INGESTION ====================
  const handleIngestText = async () => {
    if (!ingestText.trim()) return;
    setLoading(true);
    setError("");
    try {
      const res = await request("/intake/summarize", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          text: ingestText, 
          source: "kitenga-dev-hub",
          save_to_vector: true 
        }),
      });
      setIngestResults(prev => [{ type: "text", ...res, ts: new Date().toISOString() }, ...prev.slice(0, 9)]);
      setIngestText("");
    } catch (err) {
      setError(String(err));
    } finally {
      setLoading(false);
    }
  };

  const handleIngestFile = async () => {
    if (!file) return;
    setLoading(true);
    setError("");
    try {
      const formData = new FormData();
      formData.append("file", file);
      
      // Determine endpoint based on file type
      const ext = file.name.split('.').pop()?.toLowerCase();
      let endpoint = "/intake/ocr";
      if (ext === "pdf") endpoint = "/kitenga/tool/ocr";
      
      const res = await request(endpoint, {
        method: "POST",
        body: formData,
      });
      setIngestResults(prev => [{ type: "file", filename: file.name, ...res, ts: new Date().toISOString() }, ...prev.slice(0, 9)]);
      setFile(null);
    } catch (err) {
      setError(String(err));
    } finally {
      setLoading(false);
    }
  };

  // ==================== REALM GENERATOR ====================
  const handleCreateRealm = async () => {
    if (!realmName.trim() || !kaitiakiName.trim()) {
      setError("Realm name and Kaitiaki name are required");
      return;
    }
    setLoading(true);
    setError("");
    try {
      // Step 1: Create OpenAI Assistant with vector store
      const assistantRes = await request("/kitenga/db/whakapapa", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          id: `realm-${realmName.toLowerCase().replace(/\s+/g, '_')}-${Date.now()}`,
          title: `Realm: ${realmName}`,
          category: "realm_creation",
          summary: `Created realm ${realmName} with kaitiaki ${kaitiakiName}`,
          content_type: "realm",
          data: {
            realm_name: realmName,
            description: realmDescription,
            kaitiaki: {
              name: kaitiakiName,
              role: kaitiakiRole,
              instructions: kaitiakiInstructions,
            },
            created_at: new Date().toISOString(),
            status: "initialized"
          },
          author: "kitenga_whiro"
        }),
      });

      // Step 2: Log to memory
      await request("/kitenga/db/memory", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          content: `Created realm "${realmName}" with kaitiaki "${kaitiakiName}". Role: ${kaitiakiRole}`,
          metadata: { realm: realmName, kaitiaki: kaitiakiName, type: "realm_creation" }
        }),
      });

      // Step 3: Create actual OpenAI assistant (if endpoint exists)
      try {
        const openaiRes = await request("/assistant/run", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            action: "create_assistant",
            name: kaitiakiName,
            instructions: kaitiakiInstructions || `You are ${kaitiakiName}, the kaitiaki (guardian) of the ${realmName} realm. ${kaitiakiRole}`,
            model: "gpt-4o",
            tools: [{ type: "file_search" }],
            create_vector_store: true,
            vector_store_name: `${realmName}_vector_store`
          }),
        });
        
        setCreatedRealms(prev => [{
          name: realmName,
          kaitiaki: kaitiakiName,
          assistant_id: openaiRes.assistant_id,
          vector_store_id: openaiRes.vector_store_id,
          created_at: new Date().toISOString()
        }, ...prev]);
      } catch {
        // Assistant creation endpoint might not exist yet
        setCreatedRealms(prev => [{
          name: realmName,
          kaitiaki: kaitiakiName,
          logged_to: "whakapapa",
          created_at: new Date().toISOString()
        }, ...prev]);
      }

      // Clear form
      setRealmName("");
      setRealmDescription("");
      setKaitiakiName("");
      setKaitiakiRole("");
      setKaitiakiInstructions("");
      
    } catch (err) {
      setError(String(err));
    } finally {
      setLoading(false);
    }
  };

  // ==================== DATABASE ====================
  const loadDbStats = async () => {
    setLoading(true);
    try {
      const stats = await request("/kitenga/db/stats");
      setDbStats(stats);
    } catch (err) {
      setError(String(err));
    } finally {
      setLoading(false);
    }
  };

  const loadDbLogs = async () => {
    setLoading(true);
    try {
      const logs = await request("/kitenga/db/logs/recent?limit=20");
      setDbLogs(logs.logs || []);
    } catch (err) {
      setError(String(err));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (activeSection === "database") {
      loadDbStats();
    }
  }, [activeSection]);

  // ==================== RENDER ====================
  const sections = [
    { id: "vector", label: "Vector Recall", icon: "🔍" },
    { id: "web", label: "Web Search", icon: "🌐" },
    { id: "ingest", label: "Ingestion", icon: "📥" },
    { id: "realm", label: "Realm Generator", icon: "🏰" },
    { id: "database", label: "Kitenga DB", icon: "🗄️" },
  ];

  return (
    <div className="w-full h-screen flex flex-col bg-slate-950 text-slate-100">
      {/* Header */}
      <div className="border-b border-slate-700 bg-slate-900 p-3">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-emerald-400">🐺 Kitenga DevHub</h1>
            <p className="text-xs text-slate-400">Vector recall • Web search • Ingestion • Realm generator</p>
          </div>
          <span className="text-xs text-slate-500">{baseUrl}</span>
        </div>
        {error && <p className="text-red-400 text-xs mt-1">{error}</p>}
      </div>

      {/* Section Tabs */}
      <div className="flex border-b border-slate-700 bg-slate-900">
        {sections.map((section) => (
          <button
            key={section.id}
            onClick={() => setActiveSection(section.id)}
            className={`px-4 py-2 text-sm font-medium transition ${
              activeSection === section.id
                ? "border-b-2 border-emerald-500 text-emerald-400"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            <span className="mr-1">{section.icon}</span>
            {section.label}
          </button>
        ))}
      </div>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden p-3 gap-3">
        {/* Left Panel - Input */}
        <div className="w-96 flex flex-col bg-slate-900 rounded border border-slate-700 overflow-hidden">
          <div className="border-b border-slate-700 bg-slate-800 px-3 py-2">
            <h2 className="font-bold text-emerald-400 text-sm">
              {sections.find(s => s.id === activeSection)?.icon} {sections.find(s => s.id === activeSection)?.label}
            </h2>
          </div>
          <div className="flex-1 overflow-y-auto p-3 space-y-3">
            
            {/* VECTOR SECTION */}
            {activeSection === "vector" && (
              <>
                <textarea
                  className="w-full min-h-[120px] rounded border border-slate-700 bg-slate-950 p-2 text-sm"
                  placeholder="Enter query or text to embed..."
                  value={vectorQuery}
                  onChange={(e) => setVectorQuery(e.target.value)}
                />
                <div className="flex items-center gap-2">
                  <label className="text-xs text-slate-400">Top K:</label>
                  <input
                    type="number"
                    min="1"
                    max="20"
                    value={topK}
                    onChange={(e) => setTopK(Number(e.target.value))}
                    className="w-16 rounded border border-slate-700 bg-slate-950 px-2 py-1 text-sm"
                  />
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={handleVectorSearch}
                    disabled={loading}
                    className="flex-1 px-3 py-2 bg-emerald-600 hover:bg-emerald-700 disabled:bg-slate-600 rounded text-sm font-medium"
                  >
                    Search
                  </button>
                  <button
                    onClick={handleVectorEmbed}
                    disabled={loading}
                    className="flex-1 px-3 py-2 bg-sky-600 hover:bg-sky-700 disabled:bg-slate-600 rounded text-sm font-medium"
                  >
                    Embed
                  </button>
                </div>
              </>
            )}

            {/* WEB SEARCH SECTION */}
            {activeSection === "web" && (
              <>
                <textarea
                  className="w-full min-h-[100px] rounded border border-slate-700 bg-slate-950 p-2 text-sm"
                  placeholder="Enter search query..."
                  value={webQuery}
                  onChange={(e) => setWebQuery(e.target.value)}
                />
                <div className="flex gap-2">
                  <button
                    onClick={handleWebSearch}
                    disabled={loading}
                    className="flex-1 px-3 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-600 rounded text-sm font-medium"
                  >
                    Web Search
                  </button>
                  <button
                    onClick={handleStackedSearch}
                    disabled={loading}
                    className="flex-1 px-3 py-2 bg-purple-600 hover:bg-purple-700 disabled:bg-slate-600 rounded text-sm font-medium"
                  >
                    Stacked
                  </button>
                </div>
                <p className="text-xs text-slate-500">Stacked = Vector + Web combined</p>
              </>
            )}

            {/* INGESTION SECTION */}
            {activeSection === "ingest" && (
              <>
                <div className="flex gap-2 mb-2">
                  <button
                    onClick={() => setIngestType("text")}
                    className={`px-3 py-1 rounded text-xs ${ingestType === "text" ? "bg-emerald-600" : "bg-slate-700"}`}
                  >
                    Text
                  </button>
                  <button
                    onClick={() => setIngestType("file")}
                    className={`px-3 py-1 rounded text-xs ${ingestType === "file" ? "bg-emerald-600" : "bg-slate-700"}`}
                  >
                    File
                  </button>
                </div>
                
                {ingestType === "text" ? (
                  <>
                    <textarea
                      className="w-full min-h-[150px] rounded border border-slate-700 bg-slate-950 p-2 text-sm"
                      placeholder="Paste text to ingest and summarize..."
                      value={ingestText}
                      onChange={(e) => setIngestText(e.target.value)}
                    />
                    <button
                      onClick={handleIngestText}
                      disabled={loading}
                      className="w-full px-3 py-2 bg-emerald-600 hover:bg-emerald-700 disabled:bg-slate-600 rounded text-sm font-medium"
                    >
                      Ingest & Summarize
                    </button>
                  </>
                ) : (
                  <>
                    <input
                      type="file"
                      accept=".pdf,.md,.txt,.png,.jpg,.jpeg"
                      onChange={(e) => setFile(e.target.files?.[0] || null)}
                      className="w-full text-sm text-slate-400 file:mr-2 file:py-1 file:px-3 file:rounded file:border-0 file:bg-slate-700 file:text-slate-200"
                    />
                    {file && <p className="text-xs text-slate-400">Selected: {file.name}</p>}
                    <button
                      onClick={handleIngestFile}
                      disabled={loading || !file}
                      className="w-full px-3 py-2 bg-emerald-600 hover:bg-emerald-700 disabled:bg-slate-600 rounded text-sm font-medium"
                    >
                      Upload & Process
                    </button>
                    <p className="text-xs text-slate-500">Supports: PDF, MD, TXT, PNG, JPG</p>
                  </>
                )}
              </>
            )}

            {/* REALM GENERATOR SECTION */}
            {activeSection === "realm" && (
              <>
                <div className="space-y-2">
                  <input
                    type="text"
                    placeholder="Realm Name (e.g., Te Wai)"
                    value={realmName}
                    onChange={(e) => setRealmName(e.target.value)}
                    className="w-full rounded border border-slate-700 bg-slate-950 p-2 text-sm"
                  />
                  <input
                    type="text"
                    placeholder="Realm Description"
                    value={realmDescription}
                    onChange={(e) => setRealmDescription(e.target.value)}
                    className="w-full rounded border border-slate-700 bg-slate-950 p-2 text-sm"
                  />
                  <hr className="border-slate-700 my-2" />
                  <p className="text-xs text-emerald-400 font-medium">Kaitiaki (Guardian)</p>
                  <input
                    type="text"
                    placeholder="Kaitiaki Name"
                    value={kaitiakiName}
                    onChange={(e) => setKaitiakiName(e.target.value)}
                    className="w-full rounded border border-slate-700 bg-slate-950 p-2 text-sm"
                  />
                  <input
                    type="text"
                    placeholder="Kaitiaki Role"
                    value={kaitiakiRole}
                    onChange={(e) => setKaitiakiRole(e.target.value)}
                    className="w-full rounded border border-slate-700 bg-slate-950 p-2 text-sm"
                  />
                  <textarea
                    placeholder="System Instructions (optional)"
                    value={kaitiakiInstructions}
                    onChange={(e) => setKaitiakiInstructions(e.target.value)}
                    className="w-full min-h-[80px] rounded border border-slate-700 bg-slate-950 p-2 text-sm"
                  />
                </div>
                <button
                  onClick={handleCreateRealm}
                  disabled={loading}
                  className="w-full px-3 py-2 bg-cyan-600 hover:bg-cyan-700 disabled:bg-slate-600 rounded text-sm font-medium"
                >
                  🏰 Create Realm + Assistant + Vector Store
                </button>
                <p className="text-xs text-slate-500">Creates OpenAI assistant with dedicated vector store</p>
              </>
            )}

            {/* DATABASE SECTION */}
            {activeSection === "database" && (
              <>
                <button
                  onClick={loadDbStats}
                  disabled={loading}
                  className="w-full px-3 py-2 bg-slate-700 hover:bg-slate-600 rounded text-sm font-medium"
                >
                  Refresh Stats
                </button>
                <button
                  onClick={loadDbLogs}
                  disabled={loading}
                  className="w-full px-3 py-2 bg-slate-700 hover:bg-slate-600 rounded text-sm font-medium"
                >
                  Load Recent Logs
                </button>
                {dbStats && (
                  <div className="mt-2 p-2 bg-slate-800 rounded text-xs">
                    <p className="text-emerald-400 font-medium mb-1">Schema: {dbStats.schema}</p>
                    <p className="text-slate-400">Total records: {dbStats.total_records}</p>
                    <div className="mt-2 space-y-1">
                      {Object.entries(dbStats.table_counts || {}).map(([table, count]) => (
                        <div key={table} className="flex justify-between">
                          <span className="text-slate-400">{table}</span>
                          <span className="text-sky-400">{count}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </>
            )}

            {loading && <Spinner text="Processing..." />}
          </div>
        </div>

        {/* Right Panel - Results */}
        <div className="flex-1 flex flex-col bg-slate-900 rounded border border-slate-700 overflow-hidden">
          <div className="border-b border-slate-700 bg-slate-800 px-3 py-2 flex justify-between items-center">
            <h2 className="font-bold text-emerald-400 text-sm">Results</h2>
            <button
              onClick={() => {
                setVectorResults([]);
                setWebResults([]);
                setIngestResults([]);
                setDbLogs([]);
              }}
              className="text-xs text-slate-400 hover:text-slate-200"
            >
              Clear
            </button>
          </div>
          <div className="flex-1 overflow-y-auto p-3 space-y-2">
            
            {/* Vector Results */}
            {activeSection === "vector" && vectorResults.map((result, idx) => (
              <div key={idx} className="border border-slate-700 rounded p-2 bg-slate-800 text-xs">
                {result.type === "embedded" ? (
                  <div>
                    <span className="text-emerald-400">✓ Embedded</span>
                    <p className="text-slate-400 mt-1">ID: {result.id || result.file_id || "N/A"}</p>
                  </div>
                ) : (
                  <div>
                    <div className="flex justify-between mb-1">
                      <span className="text-sky-400">Score: {(result.score || result.similarity || 0).toFixed(3)}</span>
                    </div>
                    <p className="text-slate-300">{result.text || result.chunk_text || result.content || JSON.stringify(result).slice(0, 200)}</p>
                  </div>
                )}
              </div>
            ))}

            {/* Web Results */}
            {activeSection === "web" && webResults.map((result, idx) => (
              <div key={idx} className="border border-slate-700 rounded p-2 bg-slate-800 text-xs">
                <p className="text-blue-400 font-medium">{result.title || "Result"}</p>
                <p className="text-slate-400 mt-1">{result.snippet || result.description || result.content?.slice(0, 200)}</p>
                {result.url && <a href={result.url} target="_blank" rel="noopener" className="text-sky-500 hover:underline text-[10px]">{result.url}</a>}
              </div>
            ))}

            {/* Ingest Results */}
            {activeSection === "ingest" && ingestResults.map((result, idx) => (
              <div key={idx} className="border border-slate-700 rounded p-2 bg-slate-800 text-xs">
                <div className="flex justify-between mb-1">
                  <span className="text-emerald-400">{result.type === "file" ? `📄 ${result.filename}` : "📝 Text"}</span>
                  <span className="text-slate-500">{result.ts}</span>
                </div>
                <p className="text-slate-300">{result.summary || result.text || result.extracted_text?.slice(0, 300) || "Processed"}</p>
              </div>
            ))}

            {/* Created Realms */}
            {activeSection === "realm" && createdRealms.map((realm, idx) => (
              <div key={idx} className="border border-cyan-800 rounded p-2 bg-cyan-950 text-xs">
                <p className="text-cyan-400 font-medium">🏰 {realm.name}</p>
                <p className="text-slate-300">Kaitiaki: {realm.kaitiaki}</p>
                {realm.assistant_id && <p className="text-slate-400">Assistant: {realm.assistant_id}</p>}
                {realm.vector_store_id && <p className="text-slate-400">Vector Store: {realm.vector_store_id}</p>}
                <p className="text-slate-500 text-[10px]">{realm.created_at}</p>
              </div>
            ))}

            {/* Database Logs */}
            {activeSection === "database" && dbLogs.map((log, idx) => (
              <div key={idx} className="border border-slate-700 rounded p-2 bg-slate-800 text-xs">
                <div className="flex justify-between mb-1">
                  <span className="text-amber-400">{log.event}</span>
                  <span className="text-slate-500">{log.created_at}</span>
                </div>
                <p className="text-slate-300">{log.detail}</p>
                <p className="text-slate-500 text-[10px]">Source: {log.source}</p>
              </div>
            ))}

            {/* Empty state */}
            {((activeSection === "vector" && !vectorResults.length) ||
              (activeSection === "web" && !webResults.length) ||
              (activeSection === "ingest" && !ingestResults.length) ||
              (activeSection === "realm" && !createdRealms.length) ||
              (activeSection === "database" && !dbLogs.length)) && (
              <p className="text-slate-500 text-sm text-center py-8">No results yet. Use the controls on the left.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
