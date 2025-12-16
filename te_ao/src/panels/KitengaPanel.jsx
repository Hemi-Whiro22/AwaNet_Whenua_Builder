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
  const [threadId, setThreadId] = useState(() => {
    return localStorage.getItem("kitenga_thread_id") || null;
  });
  const messagesEndRef = useRef(null);
  
  // Context enrichment options
  const [useVectorContext, setUseVectorContext] = useState(true);
  const [useMemoryContext, setUseMemoryContext] = useState(true);
  const [vectorContext, setVectorContext] = useState([]);
  const [showContext, setShowContext] = useState(false);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Fetch vector context for query
  const fetchVectorContext = async (query) => {
    if (!useVectorContext) return [];
    try {
      const res = await request("/vector/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, top_k: 3, rerank: true }),
      });
      return res.matches || res.results || [];
    } catch {
      return [];
    }
  };

  // Fetch memory context
  const fetchMemoryContext = async (query) => {
    if (!useMemoryContext) return [];
    try {
      const res = await request("/memory/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, limit: 3 }),
      });
      return res.results || res.memories || [];
    } catch {
      return [];
    }
  };

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
      // Fetch context in parallel
      const [vectorResults, memoryResults] = await Promise.all([
        fetchVectorContext(input),
        fetchMemoryContext(input),
      ]);

      // Store context for display
      setVectorContext([...vectorResults, ...memoryResults]);

      // Build context string
      let contextStr = "";
      if (vectorResults.length > 0) {
        contextStr += "Vector Context:\n" + vectorResults.map(r => r.text || r.content || r.chunk_text || "").join("\n---\n") + "\n\n";
      }
      if (memoryResults.length > 0) {
        contextStr += "Memory Context:\n" + memoryResults.map(r => r.content || r.text || "").join("\n---\n") + "\n\n";
      }

      const response = await request("/kitenga/gpt-whisper", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          whisper: contextStr ? `Context:\n${contextStr}\n\nQuestion: ${input}` : input,
          session_id: "ui-kitenga",
          thread_id: threadId,
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

      if (response?.thread_id && !threadId) {
        setThreadId(response.thread_id);
        localStorage.setItem("kitenga_thread_id", response.thread_id);
      }

      const assistantMessage = {
        role: "assistant",
        content:
          response?.summary_long ||
          response?.summary ||
          response?.response ||
          "No response received",
        timestamp: new Date(),
        metadata: response,
        hasContext: vectorResults.length > 0 || memoryResults.length > 0,
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
              Māori Intelligence Engine with vector + memory context
            </p>
          </div>
          <div className="flex items-center gap-3">
            <label className="flex items-center gap-1 text-xs text-slate-400">
              <input
                type="checkbox"
                checked={useVectorContext}
                onChange={(e) => setUseVectorContext(e.target.checked)}
                className="w-3 h-3"
              />
              🔍 Vector
            </label>
            <label className="flex items-center gap-1 text-xs text-slate-400">
              <input
                type="checkbox"
                checked={useMemoryContext}
                onChange={(e) => setUseMemoryContext(e.target.checked)}
                className="w-3 h-3"
              />
              🧠 Memory
            </label>
            {vectorContext.length > 0 && (
              <button
                onClick={() => setShowContext(!showContext)}
                className="text-xs text-sky-400 hover:text-sky-300"
              >
                {showContext ? "Hide" : "Show"} Context ({vectorContext.length})
              </button>
            )}
          </div>
        </div>
        
        {/* Context Display */}
        {showContext && vectorContext.length > 0 && (
          <div className="mt-3 p-2 bg-slate-800 rounded border border-slate-700 max-h-32 overflow-y-auto">
            <p className="text-xs text-slate-400 mb-1">Context used in last query:</p>
            {vectorContext.map((ctx, idx) => (
              <p key={idx} className="text-xs text-slate-300 truncate">
                {ctx.text || ctx.content || ctx.chunk_text || JSON.stringify(ctx).slice(0, 100)}
              </p>
            ))}
          </div>
        )}
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

        {/* Clear Thread Button */}
        {threadId && (
          <button
            onClick={() => {
              setThreadId(null);
              localStorage.removeItem("kitenga_thread_id");
              setMessages([
                {
                  role: "assistant",
                  content:
                    "Kia ora 👋 I'm Kitenga Whiro, the intelligence engine for this project. I have full context about The Awa Network architecture, te_po backend, te_ao frontend, te_hau CLI, realm systems, and Kaitiaki governance. Ask me anything about the project!",
                  timestamp: new Date(),
                },
              ]);
            }}
            className="mb-3 w-full px-3 py-2 bg-red-900/30 hover:bg-red-900/50 border border-red-700 rounded text-xs text-red-300 transition"
          >
            🔄 Start New Conversation (Thread: {threadId.substring(0, 8)}...)
          </button>
        )}

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
