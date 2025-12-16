import { useState, useEffect } from "react";
import { useApi } from "../hooks/useApi.js";

/**
 * KitengaDevHub - Research & Ingestion Hub
 * Features:
 * - Live vector recall across all vector stores
 * - Web search + save to vector
 * - Document ingestion (PDF, MD, images)
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

  // Vector Search state
  const [vectorQuery, setVectorQuery] = useState("");
  const [topK, setTopK] = useState(5);
  const [vectorResults, setVectorResults] = useState([]);

  // Research & Ingest state (combined)
  const [researchQuery, setResearchQuery] = useState("");
  const [researchResults, setResearchResults] = useState([]);
  const [saveToVector, setSaveToVector] = useState(true);
  const [file, setFile] = useState(null);
  const [ingestText, setIngestText] = useState("");
  const [ingestResults, setIngestResults] = useState([]);

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

  // ==================== RESEARCH (Web + Save) ====================
  const handleWebSearch = async () => {
    if (!researchQuery.trim()) return;
    setLoading(true);
    setError("");
    try {
      const res = await request("/research/web_search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: researchQuery, num_results: 10 }),
      });
      const results = res.results || res || [];
      setResearchResults(results);
      
      // Auto-save to vector if enabled
      if (saveToVector && results.length > 0) {
        const combinedText = results.map(r => `${r.title || ''}: ${r.snippet || r.description || ''}`).join('\n\n');
        await request("/vector/embed", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ 
            text: combinedText, 
            metadata: { source: "web_search", query: researchQuery }
          }),
        });
      }
    } catch (err) {
      setError(String(err));
    } finally {
      setLoading(false);
    }
  };

  const handleStackedSearch = async () => {
    if (!researchQuery.trim()) return;
    setLoading(true);
    setError("");
    try {
      const res = await request("/research/stacked", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: researchQuery }),
      });
      setResearchResults(res.results || [res]);
    } catch (err) {
      setError(String(err));
    } finally {
      setLoading(false);
    }
  };

  const handleSaveResultToVector = async (result) => {
    setLoading(true);
    try {
      await request("/vector/embed", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          text: `${result.title || ''}\n\n${result.snippet || result.description || result.content || ''}`,
          metadata: { source: result.url || "research", title: result.title }
        }),
      });
      setError("");
      setResearchResults(prev => prev.map(r => 
        r === result ? { ...r, saved: true } : r
      ));
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

  // ==================== RENDER ====================
  const sections = [
    { id: "vector", label: "Vector Recall", icon: "🔍" },
    { id: "research", label: "Research & Save", icon: "🌐" },
    { id: "ingest", label: "Ingestion", icon: "📥" },
  ];

  return (
    <div className="w-full h-screen flex flex-col bg-slate-950 text-slate-100">
      {/* Header */}
      <div className="border-b border-slate-700 bg-slate-900 p-3">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-emerald-400">🐺 Kitenga DevHub</h1>
            <p className="text-xs text-slate-400">Vector recall • Web research • Document ingestion</p>
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
                  placeholder="Enter query to search vector stores or text to embed..."
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
                    🔍 Search
                  </button>
                  <button
                    onClick={handleVectorEmbed}
                    disabled={loading}
                    className="flex-1 px-3 py-2 bg-sky-600 hover:bg-sky-700 disabled:bg-slate-600 rounded text-sm font-medium"
                  >
                    💾 Embed
                  </button>
                </div>
              </>
            )}

            {/* RESEARCH SECTION */}
            {activeSection === "research" && (
              <>
                <textarea
                  className="w-full min-h-[100px] rounded border border-slate-700 bg-slate-950 p-2 text-sm"
                  placeholder="Enter search query..."
                  value={researchQuery}
                  onChange={(e) => setResearchQuery(e.target.value)}
                />
                <label className="flex items-center gap-2 text-xs text-slate-400">
                  <input
                    type="checkbox"
                    checked={saveToVector}
                    onChange={(e) => setSaveToVector(e.target.checked)}
                  />
                  Auto-save results to vector store
                </label>
                <div className="flex gap-2">
                  <button
                    onClick={handleWebSearch}
                    disabled={loading}
                    className="flex-1 px-3 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-600 rounded text-sm font-medium"
                  >
                    🌐 Web Search
                  </button>
                  <button
                    onClick={handleStackedSearch}
                    disabled={loading}
                    className="flex-1 px-3 py-2 bg-purple-600 hover:bg-purple-700 disabled:bg-slate-600 rounded text-sm font-medium"
                  >
                    📚 Stacked
                  </button>
                </div>
                <p className="text-xs text-slate-500">Stacked = Vector + Web combined for rich context</p>
              </>
            )}

            {/* INGESTION SECTION */}
            {activeSection === "ingest" && (
              <>
                <div className="space-y-3">
                  <div>
                    <label className="text-xs text-slate-400 block mb-1">Paste Text</label>
                    <textarea
                      className="w-full min-h-[100px] rounded border border-slate-700 bg-slate-950 p-2 text-sm"
                      placeholder="Paste text to ingest and embed..."
                      value={ingestText}
                      onChange={(e) => setIngestText(e.target.value)}
                    />
                    <button
                      onClick={handleIngestText}
                      disabled={loading || !ingestText.trim()}
                      className="w-full mt-2 px-3 py-2 bg-emerald-600 hover:bg-emerald-700 disabled:bg-slate-600 rounded text-sm font-medium"
                    >
                      📝 Ingest Text
                    </button>
                  </div>
                  
                  <div className="border-t border-slate-700 pt-3">
                    <label className="text-xs text-slate-400 block mb-1">Or Upload File</label>
                    <input
                      type="file"
                      accept=".pdf,.md,.txt,.png,.jpg,.jpeg"
                      onChange={(e) => setFile(e.target.files?.[0] || null)}
                      className="w-full text-sm text-slate-400 file:mr-2 file:py-1 file:px-3 file:rounded file:border-0 file:bg-slate-700 file:text-slate-200"
                    />
                    {file && <p className="text-xs text-slate-400 mt-1">Selected: {file.name}</p>}
                    <button
                      onClick={handleIngestFile}
                      disabled={loading || !file}
                      className="w-full mt-2 px-3 py-2 bg-sky-600 hover:bg-sky-700 disabled:bg-slate-600 rounded text-sm font-medium"
                    >
                      📄 Upload & Process
                    </button>
                    <p className="text-xs text-slate-500 mt-1">Supports: PDF, MD, TXT, PNG, JPG</p>
                  </div>
                </div>
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
                setResearchResults([]);
                setIngestResults([]);
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
                    <span className="text-emerald-400">✓ Embedded to vector store</span>
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

            {/* Research Results */}
            {activeSection === "research" && researchResults.map((result, idx) => (
              <div key={idx} className="border border-slate-700 rounded p-2 bg-slate-800 text-xs">
                <div className="flex justify-between items-start mb-1">
                  <p className="text-blue-400 font-medium flex-1">{result.title || "Result"}</p>
                  {!result.saved ? (
                    <button
                      onClick={() => handleSaveResultToVector(result)}
                      className="text-emerald-400 hover:text-emerald-300 ml-2"
                      title="Save to vector"
                    >
                      💾
                    </button>
                  ) : (
                    <span className="text-emerald-400 ml-2">✓</span>
                  )}
                </div>
                <p className="text-slate-400 mt-1">{result.snippet || result.description || result.content?.slice(0, 200)}</p>
                {result.url && <a href={result.url} target="_blank" rel="noopener" className="text-sky-500 hover:underline text-[10px] block mt-1">{result.url}</a>}
              </div>
            ))}

            {/* Ingest Results */}
            {activeSection === "ingest" && ingestResults.map((result, idx) => (
              <div key={idx} className="border border-slate-700 rounded p-2 bg-slate-800 text-xs">
                <div className="flex justify-between mb-1">
                  <span className="text-emerald-400">{result.type === "file" ? `📄 ${result.filename}` : "📝 Text"}</span>
                  <span className="text-slate-500">{result.ts}</span>
                </div>
                <p className="text-slate-300">{result.summary || result.text || result.extracted_text?.slice(0, 300) || "Processed & embedded"}</p>
              </div>
            ))}

            {/* Empty state */}
            {((activeSection === "vector" && !vectorResults.length) ||
              (activeSection === "research" && !researchResults.length) ||
              (activeSection === "ingest" && !ingestResults.length)) && (
              <p className="text-slate-500 text-sm text-center py-8">No results yet. Use the controls on the left.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
