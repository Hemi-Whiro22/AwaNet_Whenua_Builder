import { useState } from "react";
import { awa } from "../hooks/useAwa";

export default function ResearchPanel() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);

  async function runQuery() {
    const res = await awa("/research/query", {
      method: "POST",
      body: JSON.stringify({ query })
    });
    setResults(res || []);
  }

  return (
    <div className="p-4 text-white">
      <h1 className="text-2xl font-bold mb-3">Awa Research</h1>

      <input
        className="p-2 bg-gray-800 rounded mb-3 w-full"
        placeholder="Ask something..."
        onChange={(e) => setQuery(e.target.value)}
      />

      <button
        className="px-4 py-2 bg-blue-600 rounded"
        onClick={runQuery}
      >
        Search
      </button>

      <div className="mt-4 space-y-2">
        {results.map((r, i) => (
          <div key={i} className="p-3 bg-gray-900 rounded">
            <div><b>Score:</b> {r.similarity ?? "n/a"}</div>
            <div>{r.chunk_text ?? "(no text)"}</div>
          </div>
        ))}
        {!results.length && <p className="text-sm text-slate-500">No results yet.</p>}
      </div>
    </div>
  );
}
