import { useState } from "react";
import { useApi } from "../hooks/useApi";

export default function EmbedPanel() {
  const { request } = useApi();
  const [text, setText] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  async function handleEmbed() {
    try {
      setError("");
      const response = await request("/vector/embed", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      });
      setResult(response);
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="p-6 text-white space-y-4">
      <h2 className="text-2xl font-semibold">Vector Embed</h2>
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        className="w-full bg-slate-900 rounded p-3"
        rows={4}
        placeholder="Enter text to embed"
      />
      <button onClick={handleEmbed} className="bg-emerald-700 hover:bg-emerald-600 px-4 py-2 rounded">
        Embed with OpenAI
      </button>
      {error && <p className="text-red-400 text-sm">{error}</p>}
      <pre className="bg-slate-900 rounded-lg p-4 whitespace-pre-wrap text-sm">
        {result ? JSON.stringify(result, null, 2) : "No embedding run yet."}
      </pre>
    </div>
  );
}
