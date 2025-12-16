import { useEffect, useState } from "react";
import { useApi } from "../hooks/useApi.js";

export default function ApiTestPanel() {
  const { request, baseUrl } = useApi();
  const [status, setStatus] = useState(null);
  const [routes, setRoutes] = useState(null);
  const [kitengaStatus, setKitengaStatus] = useState(null);
  const [dbStats, setDbStats] = useState(null);
  const [dbLogs, setDbLogs] = useState([]);
  const [corsOrigins, setCorsOrigins] = useState([]);
  const [newOrigin, setNewOrigin] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [testResults, setTestResults] = useState([]);
  const [activeSection, setActiveSection] = useState("status");

  const loadStatus = async () => {
    setLoading(true);
    setError("");
    try {
      const [statusRes, routesRes, kitengaRes, dbStatsRes] = await Promise.all([
        request("/status/full").catch(() => null),
        request("/dev/routes").catch(() => null),
        request("/dev/kitenga-status").catch(() => null),
        request("/kitenga/db/stats").catch(() => null),
      ]);
      setStatus(statusRes);
      setRoutes(routesRes);
      setKitengaStatus(kitengaRes);
      setDbStats(dbStatsRes);
    } catch (err) {
      setError(String(err));
    } finally {
      setLoading(false);
    }
  };

  const loadDbLogs = async () => {
    try {
      const logs = await request("/kitenga/db/logs/recent?limit=20");
      setDbLogs(logs.logs || []);
    } catch (err) {
      console.log("Could not load logs:", err);
    }
  };

  const loadCorsOrigins = async () => {
    try {
      const data = await request("/cors/origins");
      setCorsOrigins(data.origins || []);
    } catch (err) {
      console.log("Could not load CORS origins:", err);
    }
  };

  const addCorsOrigin = async () => {
    if (!newOrigin.trim()) return;
    try {
      const data = await request("/cors/origins/add", {
        method: "POST",
        body: JSON.stringify({ origin: newOrigin.trim() }),
      });
      setCorsOrigins(data.origins || []);
      setNewOrigin("");
    } catch (err) {
      setError(`Failed to add origin: ${err}`);
    }
  };

  const removeCorsOrigin = async (origin) => {
    try {
      const data = await request("/cors/origins/remove", {
        method: "POST",
        body: JSON.stringify({ origin }),
      });
      setCorsOrigins(data.origins || []);
    } catch (err) {
      setError(`Failed to remove origin: ${err}`);
    }
  };

  const resetCorsOrigins = async () => {
    try {
      const data = await request("/cors/origins/reset", { method: "POST" });
      setCorsOrigins(data.origins || []);
    } catch (err) {
      setError(`Failed to reset origins: ${err}`);
    }
  };

  const runTest = async (path, method = "GET") => {
    const startTime = Date.now();
    try {
      const response = await request(path, { method });
      const duration = Date.now() - startTime;
      setTestResults((prev) => [
        {
          path,
          method,
          status: "✓",
          duration: `${duration}ms`,
          timestamp: new Date().toLocaleTimeString(),
          response: JSON.stringify(response).slice(0, 200),
        },
        ...prev.slice(0, 19),
      ]);
    } catch (err) {
      const duration = Date.now() - startTime;
      setTestResults((prev) => [
        {
          path,
          method,
          status: "✗",
          error: String(err),
          duration: `${duration}ms`,
          timestamp: new Date().toLocaleTimeString(),
        },
        ...prev.slice(0, 19),
      ]);
    }
  };

  // Quick test endpoints
  const quickTests = [
    { path: "/heartbeat", method: "GET", label: "Heartbeat" },
    { path: "/status/full", method: "GET", label: "Full Status" },
    { path: "/dev/routes", method: "GET", label: "All Routes" },
    { path: "/dev/kitenga-status", method: "GET", label: "Kitenga Status" },
    { path: "/status/openai", method: "GET", label: "OpenAI Status" },
    { path: "/pipeline/jobs/recent?limit=5", method: "GET", label: "Recent Jobs" },
    { path: "/kitenga/tools/list", method: "GET", label: "Kitenga Tools" },
    { path: "/kitenga/db/stats", method: "GET", label: "DB Stats" },
    { path: "/realms/list", method: "GET", label: "List Realms" },
    { path: "/memory/stats", method: "GET", label: "Memory Stats" },
  ];

  const renderStatusValue = (value) => {
    if (typeof value === "boolean") {
      return value ? (
        <span className="text-green-400">✓</span>
      ) : (
        <span className="text-red-400">✗</span>
      );
    }
    if (typeof value === "string") return <span className="text-blue-300 text-xs">{value}</span>;
    if (typeof value === "number") return <span className="text-yellow-300">{value}</span>;
    return <span className="text-gray-400 text-xs">{JSON.stringify(value)}</span>;
  };

  return (
    <div className="w-full h-screen flex flex-col bg-slate-950 text-slate-100">
      {/* Header */}
      <div className="border-b border-slate-700 bg-slate-900 p-3">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-emerald-400">🐺 Kitenga Whiro Dev Console</h1>
            <p className="text-xs text-slate-400">API routes, server health, and diagnostics</p>
          </div>
          <div className="flex gap-2">
            <span className="text-xs text-slate-500">{baseUrl}</span>
            <button
              onClick={loadStatus}
              disabled={loading}
              className="px-3 py-1 bg-emerald-600 hover:bg-emerald-700 disabled:bg-slate-600 rounded text-sm font-medium transition"
            >
              {loading ? "..." : "Refresh All"}
            </button>
          </div>
        </div>
        {error && <p className="text-red-400 text-xs mt-1">{error}</p>}
      </div>

      {/* Section Tabs */}
      <div className="flex border-b border-slate-700 bg-slate-900">
        {["status", "routes", "kitenga", "database", "cors", "tests"].map((section) => (
          <button
            key={section}
            onClick={() => {
              setActiveSection(section);
              if (section === "database") loadDbLogs();
              if (section === "cors") loadCorsOrigins();
            }}
            className={`px-4 py-2 text-sm font-medium transition ${
              activeSection === section
                ? "border-b-2 border-emerald-500 text-emerald-400"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            {section === "database" ? "🗄️ DB" : 
             section === "cors" ? "🔒 CORS" :
             section.charAt(0).toUpperCase() + section.slice(1)}
          </button>
        ))}
      </div>

      {/* Main content */}
      <div className="flex-1 flex overflow-hidden p-3 gap-3">
        {/* Left: Status/Routes/Kitenga Panel */}
        <div className="flex-1 flex flex-col bg-slate-900 rounded border border-slate-700 overflow-hidden">
          <div className="border-b border-slate-700 bg-slate-800 px-3 py-2">
            <h2 className="font-bold text-emerald-400 text-sm">
              {activeSection === "status" && "Service Status"}
              {activeSection === "routes" && `Routes (${routes?.total_routes || 0})`}
              {activeSection === "kitenga" && "Kitenga Whiro Config"}
              {activeSection === "database" && "Database Stats & Logs"}
              {activeSection === "cors" && "CORS Origin Manager"}
              {activeSection === "tests" && "Quick Tests"}
            </h2>
          </div>
          <div className="flex-1 overflow-y-auto p-3 space-y-2">
            {activeSection === "status" && status && (
              Object.entries(status).map(([key, value]) => (
                <div key={key} className="flex justify-between items-center border-b border-slate-800 pb-1">
                  <span className="text-slate-300 text-sm">{key}</span>
                  {renderStatusValue(value)}
                </div>
              ))
            )}

            {activeSection === "routes" && routes?.grouped && (
              Object.entries(routes.grouped).map(([prefix, prefixRoutes]) => (
                <div key={prefix} className="mb-3">
                  <h3 className="text-xs font-bold text-sky-400 mb-1">/{prefix}</h3>
                  {prefixRoutes.map((r, idx) => (
                    <div 
                      key={idx} 
                      className="flex items-center gap-2 text-xs py-1 hover:bg-slate-800 px-1 rounded cursor-pointer"
                      onClick={() => runTest(r.path, r.methods[0] || "GET")}
                    >
                      <span className={`px-1 rounded text-[10px] font-mono ${
                        r.methods.includes("POST") ? "bg-orange-800" : 
                        r.methods.includes("DELETE") ? "bg-red-800" : "bg-green-800"
                      }`}>
                        {r.methods[0] || "GET"}
                      </span>
                      <span className="text-slate-300 font-mono">{r.path}</span>
                    </div>
                  ))}
                </div>
              ))
            )}

            {activeSection === "kitenga" && kitengaStatus && (
              <>
                <div className="flex items-center gap-2 mb-3">
                  <span className="text-2xl">{kitengaStatus.glyph || "🐺"}</span>
                  <div>
                    <h3 className="font-bold text-sky-400">{kitengaStatus.name}</h3>
                    <p className="text-xs text-slate-400">{kitengaStatus.role}</p>
                  </div>
                </div>
                <p className="text-sm text-slate-300 mb-3">{kitengaStatus.purpose}</p>
                <div className="grid grid-cols-3 gap-2 mb-3">
                  <div className={`p-2 rounded text-center text-xs ${kitengaStatus.openai_configured ? "bg-green-900" : "bg-red-900"}`}>
                    OpenAI {kitengaStatus.openai_configured ? "✓" : "✗"}
                  </div>
                  <div className={`p-2 rounded text-center text-xs ${kitengaStatus.supabase_configured ? "bg-green-900" : "bg-red-900"}`}>
                    Supabase {kitengaStatus.supabase_configured ? "✓" : "✗"}
                  </div>
                  <div className={`p-2 rounded text-center text-xs ${kitengaStatus.cloudflare_configured ? "bg-green-900" : "bg-red-900"}`}>
                    Cloudflare {kitengaStatus.cloudflare_configured ? "✓" : "✗"}
                  </div>
                </div>
                <h4 className="text-xs font-bold text-slate-400 mb-1">Tools ({kitengaStatus.tools_count})</h4>
                <div className="flex flex-wrap gap-1">
                  {kitengaStatus.tools?.map((tool, idx) => (
                    <span key={idx} className="px-2 py-1 bg-slate-800 rounded text-xs">{tool}</span>
                  ))}
                </div>
              </>
            )}

            {activeSection === "tests" && (
              <div className="grid grid-cols-2 gap-2">
                {quickTests.map((test, idx) => (
                  <button
                    key={idx}
                    onClick={() => runTest(test.path, test.method)}
                    className="px-3 py-2 bg-slate-800 hover:bg-slate-700 border border-slate-600 rounded text-xs font-medium transition text-left"
                  >
                    <span className={`mr-2 px-1 rounded text-[10px] ${test.method === "POST" ? "bg-orange-800" : "bg-green-800"}`}>
                      {test.method}
                    </span>
                    {test.label}
                  </button>
                ))}
              </div>
            )}

            {activeSection === "database" && (
              <div className="space-y-3">
                {/* DB Stats */}
                {dbStats && (
                  <div className="border border-slate-700 rounded p-3 bg-slate-800">
                    <h3 className="text-emerald-400 font-bold text-sm mb-2">📊 Kitenga Schema Stats</h3>
                    <p className="text-slate-300 text-xs mb-2">Schema: <span className="text-sky-400">{dbStats.schema}</span></p>
                    <p className="text-slate-300 text-xs mb-2">Total Records: <span className="text-yellow-400">{dbStats.total_records?.toLocaleString()}</span></p>
                    {dbStats.tables && (
                      <div className="space-y-1 mt-2">
                        <p className="text-xs text-slate-400 font-medium">Tables:</p>
                        {Object.entries(dbStats.tables).map(([table, count]) => (
                          <div key={table} className="flex justify-between text-xs">
                            <span className="text-slate-300 font-mono">{table}</span>
                            <span className="text-slate-400">{count}</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
                
                {/* Recent Logs */}
                <div className="border border-slate-700 rounded p-3 bg-slate-800">
                  <div className="flex justify-between items-center mb-2">
                    <h3 className="text-amber-400 font-bold text-sm">📝 Recent Logs</h3>
                    <button 
                      onClick={loadDbLogs}
                      className="text-xs text-slate-400 hover:text-slate-200"
                    >
                      Refresh
                    </button>
                  </div>
                  {dbLogs.length > 0 ? (
                    <div className="space-y-2 max-h-64 overflow-y-auto">
                      {dbLogs.map((log, idx) => (
                        <div key={idx} className="border-b border-slate-700 pb-2 last:border-0">
                          <div className="flex justify-between text-xs">
                            <span className="text-amber-400">{log.event}</span>
                            <span className="text-slate-500">{log.created_at}</span>
                          </div>
                          <p className="text-slate-300 text-xs mt-1">{log.detail}</p>
                          <p className="text-slate-500 text-[10px]">Source: {log.source}</p>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-slate-400 text-xs">No logs loaded</p>
                  )}
                </div>
              </div>
            )}

            {activeSection === "cors" && (
              <div className="space-y-3">
                <div className="border border-slate-700 rounded p-3 bg-slate-800">
                  <div className="flex justify-between items-center mb-3">
                    <h3 className="text-emerald-400 font-bold text-sm">🔒 CORS Allowed Origins</h3>
                    <button 
                      onClick={resetCorsOrigins}
                      className="text-xs text-slate-400 hover:text-red-400"
                    >
                      Reset to defaults
                    </button>
                  </div>
                  
                  {/* Add new origin */}
                  <div className="flex gap-2 mb-3">
                    <input
                      type="text"
                      value={newOrigin}
                      onChange={(e) => setNewOrigin(e.target.value)}
                      placeholder="http://localhost:5002"
                      className="flex-1 bg-slate-900 border border-slate-600 rounded px-2 py-1 text-sm focus:outline-none focus:border-emerald-500"
                      onKeyDown={(e) => e.key === "Enter" && addCorsOrigin()}
                    />
                    <button
                      onClick={addCorsOrigin}
                      className="px-3 py-1 bg-emerald-600 hover:bg-emerald-700 rounded text-sm font-medium"
                    >
                      Add
                    </button>
                  </div>

                  {/* Origins list */}
                  <div className="space-y-1 max-h-64 overflow-y-auto">
                    {corsOrigins.length > 0 ? (
                      corsOrigins.map((origin, idx) => (
                        <div key={idx} className="flex justify-between items-center bg-slate-900 rounded px-2 py-1 group">
                          <span className="text-slate-300 text-xs font-mono">{origin}</span>
                          <button
                            onClick={() => removeCorsOrigin(origin)}
                            className="text-slate-500 hover:text-red-400 opacity-0 group-hover:opacity-100 transition"
                          >
                            ✕
                          </button>
                        </div>
                      ))
                    ) : (
                      <p className="text-slate-400 text-xs">Click CORS tab to load origins</p>
                    )}
                  </div>
                </div>

                <div className="border border-amber-800 rounded p-3 bg-amber-950/30">
                  <p className="text-amber-400 text-xs">
                    ⚠️ <strong>Note:</strong> Runtime CORS changes only persist until server restart. 
                    For permanent changes, update <code className="bg-slate-800 px-1 rounded">CORS_ALLOW_ORIGINS</code> env var on Render.
                  </p>
                </div>

                {/* Quick add common ports */}
                <div className="border border-slate-700 rounded p-3 bg-slate-800">
                  <h4 className="text-slate-400 text-xs font-medium mb-2">Quick Add Common Ports</h4>
                  <div className="flex flex-wrap gap-1">
                    {["3000", "4000", "5000", "5001", "5173", "8080", "8100"].map((port) => (
                      <button
                        key={port}
                        onClick={() => setNewOrigin(`http://localhost:${port}`)}
                        className="px-2 py-1 bg-slate-700 hover:bg-slate-600 rounded text-xs"
                      >
                        :{port}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {!status && !routes && !kitengaStatus && activeSection !== "tests" && activeSection !== "database" && activeSection !== "cors" && (
              <p className="text-slate-400 text-sm">Click "Refresh All" to load data</p>
            )}
          </div>
        </div>

        {/* Right: Test Results */}
        <div className="w-80 flex flex-col bg-slate-900 rounded border border-slate-700 overflow-hidden">
          <div className="border-b border-slate-700 bg-slate-800 px-3 py-2 flex justify-between items-center">
            <h2 className="font-bold text-emerald-400 text-sm">Test Results</h2>
            <button 
              onClick={() => setTestResults([])}
              className="text-xs text-slate-400 hover:text-slate-200"
            >
              Clear
            </button>
          </div>
          <div className="flex-1 overflow-y-auto p-2 space-y-2">
            {testResults.length > 0 ? (
              testResults.map((result, idx) => (
                <div
                  key={idx}
                  className={`border rounded p-2 text-xs font-mono ${
                    result.status === "✓"
                      ? "border-green-800 bg-green-950"
                      : "border-red-800 bg-red-950"
                  }`}
                >
                  <div className="flex justify-between items-center mb-1">
                    <span className="font-bold">{result.status} {result.path}</span>
                    <span className="text-slate-400">{result.duration}</span>
                  </div>
                  {result.response && (
                    <div className="text-slate-400 text-[10px] truncate">{result.response}</div>
                  )}
                  {result.error && <div className="text-red-300 text-[10px]">{result.error}</div>}
                </div>
              ))
            ) : (
              <p className="text-slate-400 text-xs">Click routes or tests to see results</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
