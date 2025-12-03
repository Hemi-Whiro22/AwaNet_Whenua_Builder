import { useState } from "react";
import { useApi } from "../hooks/useApi";

export default function OpenAIResults() {
  const { request } = useApi();
  const [results, setResults] = useState([]);
  const [error, setError] = useState("");

  async function runOpenAI() {
    try {
      setError("");
      const response = await request("/dev/openai");
      setResults(response.openai || []);
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="p-6 text-white space-y-4">
      <h2 className="text-2xl font-semibold">OpenAI Summaries</h2>
      <button onClick={runOpenAI} className="bg-emerald-700 hover:bg-emerald-600 px-4 py-2 rounded">
        Summarise Chunks
      </button>
      {error && <p className="text-red-400 text-sm">{error}</p>}
      <div className="space-y-3">
        {results.map((result, idx) => (
          <pre key={idx} className="bg-slate-900 rounded-lg p-4 whitespace-pre-wrap text-sm">
            {result}
          </pre>
        ))}
      </div>
    </div>
  );
}
