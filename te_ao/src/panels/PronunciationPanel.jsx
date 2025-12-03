import { useState } from "react";

export default function PronunciationPanel() {
  const [name, setName] = useState("");
  const [result, setResult] = useState(null);

  async function fetchPronunciation() {
    const res = await fetch("http://localhost:8000/reo/pronounce", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: name }),
    });

    const data = await res.json();
    setResult(data);
  }

  return (
    <div>
      <h2 className="text-2xl font-semibold mb-4">Pronunciation</h2>

      <input
        className="w-full p-4 bg-stone rounded mb-4"
        placeholder="Enter a Māori name or kupu..."
        value={name}
        onChange={(e) => setName(e.target.value)}
      />

      <button
        onClick={fetchPronunciation}
        className="px-6 py-3 bg-awa rounded shadow-lg"
      >
        Analyse
      </button>

      {result && (
        <div className="mt-6 p-4 bg-stone rounded">
          <h3 className="text-lg font-bold mb-2">Result:</h3>
          <p>{result.output || "No result"}</p>
        </div>
      )}
    </div>
  );
}
