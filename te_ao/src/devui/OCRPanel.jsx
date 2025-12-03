import { useState } from "react";
import { useApi } from "../hooks/useApi";

export default function OCRPanel() {
  const [output, setOutput] = useState("");
  const [error, setError] = useState("");
  const { request } = useApi();

  async function handleUpload(event) {
    const file = event.target.files?.[0];
    if (!file) return;
    const formData = new FormData();
    formData.append("file", file);
    try {
      setError("");
      setOutput("Processing…");
      const result = await request("/dev/ocr", { method: "POST", body: formData });
      setOutput(result.ocr || JSON.stringify(result, null, 2));
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="p-6 space-y-4 text-white">
      <h2 className="text-2xl font-semibold">Developer OCR</h2>
      <input type="file" onChange={handleUpload} className="text-white" />
      {error && <p className="text-red-400 text-sm">{error}</p>}
      <pre className="bg-slate-900 rounded-lg p-4 whitespace-pre-wrap text-sm">{output}</pre>
    </div>
  );
}
