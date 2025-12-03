import { useState } from "react";

export default function TranslationPanel() {
  const [text, setText] = useState("");
  const [result, setResult] = useState("");

  async function doTranslate() {
    const res = await fetch("http://localhost:8000/reo/translate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });

    const data = await res.json();
    setResult(data?.output || data?.translation || "Translation error.");
  }

  return (
    <div>
      <h2 className="text-2xl font-semibold mb-4">Reo Translation</h2>

      <textarea
        className="w-full h-40 p-4 bg-stone rounded mb-4"
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Enter text..."
      />

      <button
        onClick={doTranslate}
        className="px-6 py-3 bg-awa rounded shadow-lg"
      >
        Translate
      </button>

      {result && (
        <div className="mt-6 p-4 bg-stone rounded">
          <h3 className="text-lg font-bold mb-2">Result:</h3>
          <p>{result}</p>
        </div>
      )}
    </div>
  );
}
