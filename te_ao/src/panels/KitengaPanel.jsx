import { useEffect, useState, useRef } from "react";
import { useApi } from "../hooks/useApi.js";

const Spinner = () => (
  <div className="flex items-center gap-2 text-sm text-sky-400">
    <span className="h-3 w-3 animate-spin rounded-full border-2 border-sky-400 border-t-transparent" />
    <span>Kitenga is thinking...</span>
  </div>
);

export default function KitengaPanel() {
  const { request } = useApi();
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content:
        "Kia ora 👋 I'm Kitenga Whiro, the intelligence engine for this project. I have full context about The Awa Network architecture, te_po backend, te_ao frontend, te_hau CLI, realm systems, and Kaitiaki governance. Ask me anything about the project!",
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = {
      role: "user",
      content: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);
    setError("");

    try {
      const response = await request("/kitenga/gpt-whisper", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          whisper: input,
          session_id: "ui-kitenga",
          use_retrieval: true,
          run_pipeline: false,
          save_vector: true,
          use_openai_summary: false,
          use_openai_translation: false,
          mode: "research",
          allow_taonga_store: false,
          source: "kitenga-ui",
        }),
      });

      const assistantMessage = {
        role: "assistant",
        content:
          response?.summary_long ||
          response?.summary ||
          response?.response ||
          "No response received",
        timestamp: new Date(),
        metadata: response,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      setError(String(err));
      const errorMessage = {
        role: "assistant",
        content: `❌ Error: ${String(err)}`,
        timestamp: new Date(),
        isError: true,
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full h-screen flex flex-col bg-slate-950 text-slate-100">
      {/* Header */}
      <div className="border-b border-slate-700 bg-slate-900 p-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-sky-400 flex items-center gap-2">
              🧠 Kitenga Whiro
              <span className="text-xs bg-sky-900 text-sky-200 px-2 py-1 rounded">
                Full Project Context
              </span>
            </h1>
            <p className="text-sm text-slate-400">
              Māori Intelligence Engine with complete architecture knowledge
            </p>
          </div>
        </div>
      </div>

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-2xl px-4 py-3 rounded-lg ${
                msg.role === "user"
                  ? "bg-sky-900 text-sky-100 border border-sky-700"
                  : msg.isError
                  ? "bg-red-950 text-red-100 border border-red-700"
                  : "bg-slate-800 text-slate-100 border border-slate-700"
              }`}
            >
              <div className="text-sm leading-relaxed whitespace-pre-wrap">
                {msg.content}
              </div>
              <div
                className={`text-xs mt-2 ${
                  msg.role === "user" ? "text-sky-300" : "text-slate-400"
                }`}
              >
                {msg.timestamp.toLocaleTimeString()}
              </div>
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-slate-800 border border-slate-700 rounded-lg px-4 py-3">
              <Spinner />
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="border-t border-slate-700 bg-slate-900 p-4">
        {error && (
          <div className="mb-3 p-2 bg-red-950 border border-red-700 rounded text-sm text-red-300">
            {error}
          </div>
        )}
        <form onSubmit={sendMessage} className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask Kitenga about the project architecture, realms, APIs, etc..."
            disabled={loading}
            className="flex-1 px-4 py-2 bg-slate-800 border border-slate-600 rounded text-sm focus:outline-none focus:border-sky-500 focus:ring-1 focus:ring-sky-500 disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="px-4 py-2 bg-sky-600 hover:bg-sky-700 disabled:bg-slate-600 rounded font-medium transition"
          >
            Send
          </button>
        </form>

        {/* Quick Prompts */}
        <div className="mt-3 grid grid-cols-2 gap-2 text-xs">
          <button
            onClick={() => setInput("Explain the realm system architecture")}
            disabled={loading}
            className="px-3 py-1 bg-slate-800 hover:bg-slate-700 border border-slate-600 rounded transition disabled:opacity-50"
          >
            Realm System
          </button>
          <button
            onClick={() => setInput("What are the main components of te_po?")}
            disabled={loading}
            className="px-3 py-1 bg-slate-800 hover:bg-slate-700 border border-slate-600 rounded transition disabled:opacity-50"
          >
            Te Pó Backend
          </button>
          <button
            onClick={() => setInput("How does Kaitiaki governance work?")}
            disabled={loading}
            className="px-3 py-1 bg-slate-800 hover:bg-slate-700 border border-slate-600 rounded transition disabled:opacity-50"
          >
            Kaitiaki
          </button>
          <button
            onClick={() => setInput("What is the current project status?")}
            disabled={loading}
            className="px-3 py-1 bg-slate-800 hover:bg-slate-700 border border-slate-600 rounded transition disabled:opacity-50"
          >
            Project Status
          </button>
        </div>
      </div>
    </div>
  );
}
