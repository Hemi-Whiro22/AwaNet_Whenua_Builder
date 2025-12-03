import { useState } from "react";
import { useApi } from "../hooks/useApi";

export default function SummaryPanel() {
  const { request } = useApi();
  const [text, setText] = useState("");
  const [output, setOutput] = useState("");
  const [mode, setMode] = useState("research");
  const [error, setError] = useState("");

  async function handleSummarise() {
    try {
      setError("");
      const body = new URLSearchParams({ text, mode });
      const response = await request("/dev/summarise", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body,
      });
      setOutput(response.summary || JSON.stringify(response, null, 2));
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="p-6 text-white space-y-4">
      <h2 className="text-2xl font-semibold">Summarise</h2>
      <div className="flex gap-4">
        <select
          value={mode}
          onChange={(e) => setMode(e.target.value)}
          className="bg-slate-900 rounded p-2 border border-slate-700"
        >
          <option value="research">Research</option>
          <option value="taonga">Taonga</option>
        </select>
      </div>
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        className="w-full bg-slate-900 rounded p-3"
        rows={4}
        placeholder="Enter text to summarise"
      />
      <button onClick={handleSummarise} className="bg-emerald-700 hover:bg-emerald-600 px-4 py-2 rounded">
        Summarise
      </button>
      {error && <p className="text-red-400 text-sm">{error}</p>}
      <pre className="bg-slate-900 rounded-lg p-4 whitespace-pre-wrap text-sm">{output}</pre>
    </div>
  );
}
