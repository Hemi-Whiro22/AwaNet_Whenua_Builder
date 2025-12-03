import { useState } from "react";

export default function CulturalScanPanel() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);

  async function uploadDoc() {
    if (!file) {
      setResult({ error: "Please select a file first." });
      return;
    }

    const fd = new FormData();
    fd.append("file", file);

    // Placeholder: backend endpoint to be implemented
    const res = await fetch("http://localhost:8000/reo/scan", {
      method: "POST",
      body: fd,
    });

    const data = await res.json();
    setResult(data);
  }

  return (
    <div>
      <h2 className="text-2xl font-semibold mb-4">Cultural Document Scan</h2>

      <input
        type="file"
        onChange={(e) => setFile(e.target.files[0])}
        className="mb-4"
      />

      <button
        onClick={uploadDoc}
        className="px-6 py-3 bg-awa rounded shadow-lg"
      >
        Scan
      </button>

      {result && (
        <pre className="mt-6 p-4 bg-stone rounded text-sm">
          {JSON.stringify(result, null, 2)}
        </pre>
      )}
    </div>
  );
}
