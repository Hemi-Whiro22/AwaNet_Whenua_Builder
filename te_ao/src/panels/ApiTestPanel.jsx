import { useEffect, useState } from "react";
import { useApi } from "../hooks/useApi.js";

export default function ApiTestPanel() {
  const { request, baseUrl } = useApi();
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [testResults, setTestResults] = useState([]);

  useEffect(() => {
    loadStatus();
  }, []);

  const loadStatus = async () => {
    setLoading(true);
    setError("");
    try {
      const response = await request("/status/full");
      setStatus(response);
    } catch (err) {
      setError(String(err));
    } finally {
      setLoading(false);
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
        },
        ...prev.slice(0, 9),
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
        ...prev.slice(0, 9),
      ]);
    }
  };

  const renderStatusValue = (value) => {
    if (typeof value === "boolean") {
      return value ? (
        <span className="text-green-400">✓ Yes</span>
      ) : (
        <span className="text-red-400">✗ No</span>
      );
    }
    if (typeof value === "string") return <span className="text-blue-300">{value}</span>;
    if (typeof value === "number") return <span className="text-yellow-300">{value}</span>;
    return <span className="text-gray-400">{JSON.stringify(value)}</span>;
  };

  return (
    <div className="w-full h-screen flex flex-col bg-slate-950 text-slate-100">
      {/* Header */}
      <div className="border-b border-slate-700 bg-slate-900 p-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-emerald-400">API Health & Routes</h1>
            <p className="text-sm text-slate-400">Test endpoint health and current Render status</p>
          </div>
          <button
            onClick={loadStatus}
            disabled={loading}
            className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 disabled:bg-slate-600 rounded font-medium transition"
          >
            {loading ? "Loading..." : "Refresh Status"}
          </button>
        </div>
        {error && <p className="text-red-400 text-sm mt-2">{error}</p>}
      </div>

      {/* Main content */}
      <div className="flex-1 flex gap-4 overflow-hidden p-4">
        {/* Status Panel */}
        <div className="flex-1 flex flex-col bg-slate-900 rounded border border-slate-700 overflow-hidden">
          <div className="border-b border-slate-700 bg-slate-800 px-4 py-3">
            <h2 className="font-bold text-emerald-400">Service Status</h2>
          </div>
          <div className="flex-1 overflow-y-auto p-4 space-y-3">
            {status ? (
              Object.entries(status).map(([key, value]) => (
                <div key={key} className="border border-slate-700 rounded p-3 bg-slate-800">
                  <div className="flex justify-between items-center">
                    <span className="text-slate-300 font-medium">{key}</span>
                    {renderStatusValue(value)}
                  </div>
                </div>
              ))
            ) : (
              <p className="text-slate-400 text-sm">No status data yet</p>
            )}
          </div>
        </div>

        {/* Test Routes Panel */}
        <div className="flex-1 flex flex-col bg-slate-900 rounded border border-slate-700 overflow-hidden">
          <div className="border-b border-slate-700 bg-slate-800 px-4 py-3">
            <h2 className="font-bold text-emerald-400">Test Routes</h2>
          </div>
          <div className="flex-1 overflow-y-auto p-4 space-y-2">
            <button
              onClick={() => runTest("/heartbeat")}
              className="w-full px-3 py-2 bg-slate-800 hover:bg-slate-700 border border-slate-600 rounded text-sm font-medium transition"
            >
              /heartbeat
            </button>
            <button
              onClick={() => runTest("/status/full")}
              className="w-full px-3 py-2 bg-slate-800 hover:bg-slate-700 border border-slate-600 rounded text-sm font-medium transition"
            >
              /status/full
            </button>
            <button
              onClick={() => runTest("/docs")}
              className="w-full px-3 py-2 bg-slate-800 hover:bg-slate-700 border border-slate-600 rounded text-sm font-medium transition"
            >
              /docs (OpenAPI)
            </button>
            <button
              onClick={() => runTest("/")}
              className="w-full px-3 py-2 bg-slate-800 hover:bg-slate-700 border border-slate-600 rounded text-sm font-medium transition"
            >
              / (Root)
            </button>
            <hr className="border-slate-700 my-3" />
            <button
              onClick={() => runTest("/api/intake", "POST")}
              className="w-full px-3 py-2 bg-slate-800 hover:bg-slate-700 border border-orange-600 rounded text-sm font-medium transition"
            >
              /api/intake (POST - requires auth)
            </button>
            <button
              onClick={() => runTest("/api/chat", "POST")}
              className="w-full px-3 py-2 bg-slate-800 hover:bg-slate-700 border border-orange-600 rounded text-sm font-medium transition"
            >
              /api/chat (POST - requires auth)
            </button>
          </div>
        </div>

        {/* Test Results */}
        <div className="flex-1 flex flex-col bg-slate-900 rounded border border-slate-700 overflow-hidden">
          <div className="border-b border-slate-700 bg-slate-800 px-4 py-3">
            <h2 className="font-bold text-emerald-400">Test Results</h2>
          </div>
          <div className="flex-1 overflow-y-auto p-4 space-y-2">
            {testResults.length > 0 ? (
              testResults.map((result, idx) => (
                <div
                  key={idx}
                  className={`border rounded p-2 text-xs font-mono ${
                    result.status === "✓"
                      ? "border-green-700 bg-green-950"
                      : "border-red-700 bg-red-950"
                  }`}
                >
                  <div className="flex justify-between items-center mb-1">
                    <span className="font-bold">{result.status} {result.path}</span>
                    <span className="text-slate-400">{result.timestamp}</span>
                  </div>
                  <div className="text-slate-300">
                    {result.method} · {result.duration}
                  </div>
                  {result.error && <div className="text-red-300 mt-1">{result.error}</div>}
                </div>
              ))
            ) : (
              <p className="text-slate-400 text-sm">Run tests to see results</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
