import { useState } from "react";
import { useApi } from "../hooks/useApi";

export default function CleanPanel() {
  const { request } = useApi();
  const [output, setOutput] = useState("");
  const [error, setError] = useState("");

  async function runClean() {
    try {
      setError("");
      const result = await request("/dev/clean");
      setOutput(result.clean || JSON.stringify(result, null, 2));
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="p-6 text-white space-y-4">
      <h2 className="text-2xl font-semibold">Clean Text</h2>
      <button onClick={runClean} className="bg-emerald-700 hover:bg-emerald-600 px-4 py-2 rounded">
        Run Cleaner
      </button>
      {error && <p className="text-red-400 text-sm">{error}</p>}
      <pre className="bg-slate-900 rounded-lg p-4 whitespace-pre-wrap text-sm">{output}</pre>
    </div>
  );
}
