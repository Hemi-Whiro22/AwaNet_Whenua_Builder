import React from "react";

const BUTTON_CLASS =
  "w-full bg-slate-800 hover:bg-emerald-700 transition rounded-lg px-4 py-3 text-left font-semibold";

export default function DevMenu({ setPanel }) {
  return (
    <div className="p-6 text-white space-y-4">
      <h1 className="text-3xl font-bold text-emerald-200">Awa Developer Cockpit</h1>
      <p className="text-sm text-slate-300">
        Trigger each stage of the Te Pō pipeline locally. Start with OCR and follow the flow through OpenAI.
      </p>
      <div className="space-y-3">
        <button onClick={() => setPanel("ocr")} className={BUTTON_CLASS}>
          Run OCR
        </button>
        <button onClick={() => setPanel("clean")} className={BUTTON_CLASS}>
          Clean
        </button>
        <button onClick={() => setPanel("chunk")} className={BUTTON_CLASS}>
          Chunk
        </button>
        <button onClick={() => setPanel("openai")} className={BUTTON_CLASS}>
          OpenAI
        </button>
        <button onClick={() => setPanel("translate")} className={BUTTON_CLASS}>
          Translate
        </button>
        <button onClick={() => setPanel("summary")} className={BUTTON_CLASS}>
          Summarise
        </button>
        <button onClick={() => setPanel("embed")} className={BUTTON_CLASS}>
          Embed
        </button>
      </div>
    </div>
  );
}
