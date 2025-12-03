import { useState } from "react";
import { useApi } from "../hooks/useApi";

export default function ChunkPanel() {
  const { request } = useApi();
  const [chunks, setChunks] = useState([]);
  const [error, setError] = useState("");

  async function runChunk() {
    try {
      setError("");
      const result = await request("/dev/chunk");
      setChunks(result.chunks || []);
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="p-6 text-white space-y-4">
      <h2 className="text-2xl font-semibold">Chunk Document</h2>
      <button onClick={runChunk} className="bg-emerald-700 hover:bg-emerald-600 px-4 py-2 rounded">
        Chunk Text
      </button>
      {error && <p className="text-red-400 text-sm">{error}</p>}
      <div className="space-y-3">
        {chunks.map((chunk, idx) => (
          <pre key={idx} className="bg-slate-900 rounded-lg p-4 whitespace-pre-wrap text-sm">
            {chunk}
          </pre>
        ))}
      </div>
    </div>
  );
}
