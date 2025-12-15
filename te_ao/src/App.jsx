import { useState } from "react";
import ApiTestPanel from "./panels/ApiTestPanel";
import RealmStarterPanel from "./panels/RealmStarterPanel";
import RealmHealthPanel from "./panels/RealmHealthPanel";

export default function App() {
  const [activeTab, setActiveTab] = useState("api");

  const tabs = [
    { id: "api", label: "API & Health", icon: "⚡" },
    { id: "realms", label: "Realm Starter", icon: "🌍" },
    { id: "health", label: "Realm Events", icon: "📡" },
  ];

  return (
    <div className="w-screen h-screen flex flex-col bg-slate-950 text-slate-100">
      {/* Tab Navigation */}
      <div className="border-b border-slate-700 bg-slate-900 flex">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex-1 px-4 py-3 text-center font-medium transition border-b-2 ${
              activeTab === tab.id
                ? "border-emerald-500 text-emerald-400 bg-slate-800"
                : "border-transparent text-slate-400 hover:text-slate-300"
            }`}
          >
            <span className="mr-2">{tab.icon}</span>
            {tab.label}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-hidden">
        {activeTab === "api" && <ApiTestPanel />}
        {activeTab === "realms" && <RealmStarterPanel />}
        {activeTab === "health" && <RealmHealthPanel />}
      </div>
    </div>
  );
}

