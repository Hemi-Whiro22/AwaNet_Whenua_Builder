import { useState } from "react";
import OCRPanel from "./panels/OCRPanel";
import SummaryPanel from "./panels/SummaryPanel";
import ReoPanel from "./panels/ReoPanel";
import VectorSearchPanel from "./panels/VectorSearchPanel";
import RealmHealthPanel from "./panels/RealmHealthPanel";
import ResearchPanel from "./panels/ResearchPanel";
import ChatPanel from "./panels/ChatPanel";
import DevCockpit from "./devui/DevCockpit";

const PANELS = {
  ocr: { title: "OCR", component: <OCRPanel /> },
  summary: { title: "Summary", component: <SummaryPanel /> },
  reo: { title: "Reo Tools", component: <ReoPanel /> },
  vector: { title: "Vector Search", component: <VectorSearchPanel /> },
  realm_health: { title: "Realm Health", component: <RealmHealthPanel /> },
  research: { title: "Research", component: <ResearchPanel /> },
  chat: { title: "Assistant Chat", component: <ChatPanel /> },
  dev: { title: "Developer Cockpit", component: <DevCockpit /> },
};

export default function App() {
  const [panel, setPanel] = useState("ocr");

  return (
    <div className="min-h-screen bg-slate-950 text-white flex">
      <aside className="w-64 bg-slate-900 border-r border-slate-800 p-6 flex flex-col gap-3">
        <h1 className="text-3xl font-bold text-emerald-200 mb-4">Kitenga Whiro</h1>
        {Object.entries(PANELS).map(([key, value]) => (
          <button
            key={key}
            className={`w-full rounded-lg px-4 py-3 text-left text-sm font-semibold transition ${
              panel === key ? "bg-emerald-700 text-white" : "bg-slate-800 text-slate-200 hover:bg-slate-700"
            }`}
            onClick={() => setPanel(key)}
          >
            {value.title}
          </button>
        ))}
      </aside>
      <main className="flex-1 p-8 bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
        {PANELS[panel]?.component}
      </main>
    </div>
  );
}
