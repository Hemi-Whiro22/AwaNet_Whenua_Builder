import { useState } from "react";
import DevMenu from "./DevMenu";
import OCRPanel from "./OCRPanel";
import CleanPanel from "./CleanPanel";
import ChunkPanel from "./ChunkPanel";
import OpenAIResults from "./OpenAIResults";
import TranslatePanel from "./TranslatePanel";
import SummaryPanel from "./SummaryPanel";
import EmbedPanel from "./EmbedPanel";

const PANELS = {
  ocr: OCRPanel,
  clean: CleanPanel,
  chunk: ChunkPanel,
  openai: OpenAIResults,
  translate: TranslatePanel,
  summary: SummaryPanel,
  embed: EmbedPanel,
};

export default function DevCockpit() {
  const [panel, setPanel] = useState("menu");
  const ActivePanel = PANELS[panel];

  if (panel === "menu") {
    return <DevMenu setPanel={setPanel} />;
  }

  return (
    <div className="p-6 text-white space-y-4">
      <button
        onClick={() => setPanel("menu")}
        className="text-sm text-emerald-300 hover:text-emerald-200 underline"
      >
        ← Back to menu
      </button>
      {ActivePanel ? <ActivePanel /> : <DevMenu setPanel={setPanel} />}
    </div>
  );
}
