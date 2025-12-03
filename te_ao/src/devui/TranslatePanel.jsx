import { useState } from "react";
import { useApi } from "../hooks/useApi";

export default function TranslatePanel() {
  const { request } = useApi();
  const [text, setText] = useState("");
  const [output, setOutput] = useState("");
  const [error, setError] = useState("");

  async function handleTranslate() {
    try {
      setError("");
      const response = await request("/reo/translate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      });
      setOutput(response.output || JSON.stringify(response, null, 2));
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="p-6 text-white space-y-4">
      <h2 className="text-2xl font-semibold">Translate</h2>
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        className="w-full bg-slate-900 rounded p-3"
        rows={4}
        placeholder="Enter text to translate"
      />
      <button onClick={handleTranslate} className="bg-emerald-700 hover:bg-emerald-600 px-4 py-2 rounded">
        Translate
      </button>
      {error && <p className="text-red-400 text-sm">{error}</p>}
      <pre className="bg-slate-900 rounded-lg p-4 whitespace-pre-wrap text-sm">{output}</pre>
    </div>
  );
}
