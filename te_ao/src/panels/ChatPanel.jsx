import { useEffect, useState, useMemo } from "react";
import { useApi } from "../hooks/useApi.js";
import { v4 as uuidv4 } from "uuid";
import KitengaShell from "../layouts/KitengaShell";
import ChatMessage from "../components/chat/ChatMessage";
import ToolResultCard from "../components/chat/ToolResultCard";

const Spinner = () => (
  <div className="flex items-center gap-2 text-sm text-primary">
    <span className="h-4 w-4 animate-spin rounded-full border-2 border-primary border-t-transparent" />
    <span>Thinking...</span>
  </div>
);

export default function ChatPanel({ className = "" }) {
  const SUMMARY_WORDS = 600;
  const { request, baseUrl } = useApi();
  const callApi = useMemo(() => request, [request]); // helper alias

  const [prompt, setPrompt] = useState("");
  const [lastReply, setLastReply] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [mode, setMode] = useState("research");
  const useSummary = true; // always on
  const useTranslation = false; // handled via Translate button instead of toggle
  const allowTaongaStore = true; // taonga stored when mode=taonga
  const [threadId, setThreadId] = useState(null);
  const [status, setStatus] = useState(null);
  const [file, setFile] = useState(null);
  const [fileName, setFileName] = useState("");
  const useKaitiakiTone = true; // always on
  const useReasoning = true; // always on
  const sessionId = "ui-chat";
  const [responses, setResponses] = useState([]);
  const [profiles, setProfiles] = useState([]);
  const useRetrieval = Boolean(status?.openai_ok && status?.vector_status);

  const renderReplyText = (reply) => {
    if (!reply) return "(no reply content)";
    if (reply.summary_long) return reply.summary_long;
    if (reply.summary) return reply.summary;
    if (reply.response && typeof reply.response === "string") return reply.response;
    if (reply.translation) return reply.translation;
    if (reply.response && typeof reply.response === "object") {
      try {
        return JSON.stringify(reply.response, null, 2);
      } catch (e) {
        return String(reply.response);
      }
    }
    return reply.translation || reply.response || "(no reply content)";
  };

  useEffect(() => {
    const savedThread = localStorage.getItem("kaitiaki_thread_id");
    if (savedThread) setThreadId(savedThread);
  }, []);

  useEffect(() => {
    let mounted = true;
    const loadStatus = async () => {
      try {
        const s = await request("/status/full");
        if (!mounted) return;
        setStatus(s);
      } catch {
        if (!mounted) setStatus(null);
      }
      try {
        const recent = await request("/documents/profiles?limit=10");
        if (mounted) setProfiles(recent?.profiles || []);
      } catch {
        if (mounted) setProfiles([]);
      }
    };
    loadStatus();
    return () => {
      mounted = false;
    };
  }, [request]);

  const buildContext = async (queryText) => {
    const snippets = [];
    // Recent chat turns (local session)
    const recentChat = responses.slice(0, 4);
    if (recentChat.length) {
      const chatLines = recentChat
        .map((entry) => {
          const promptText = (entry.prompt || "").slice(0, 200);
          const replyText = (() => {
            const r = entry.reply || {};
            if (r.summary) return r.summary.slice(0, 200);
            if (r.response && typeof r.response === "string") return r.response.slice(0, 200);
            if (typeof r.translation === "string") return r.translation.slice(0, 200);
            return "";
          })();
          return `User: ${promptText}${replyText ? ` | Assistant: ${replyText}` : ""}`;
        })
        .join("\n");
      if (chatLines) snippets.push(`Recent chat:\n${chatLines}`);
    }
    try {
      const vector = await callApi("/vector/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: queryText || "", top_k: 3 }),
      });
      const matches = vector?.matches || vector?.results || [];
      matches.slice(0, 3).forEach((m, idx) => {
        const txt = typeof m?.text === "string" ? m.text.slice(0, 400) : m?.text;
        snippets.push(`Vector ${idx + 1}: ${txt || JSON.stringify(m).slice(0, 200)}`);
      });
    } catch {
      /* ignore */
    }
    try {
      const docs = await callApi("/documents/profiles?limit=3");
      (docs?.profiles || []).slice(0, 3).forEach((p, idx) => {
        const title = p.title || p.raw_path || p.clean_path || "doc";
        const summary = p.summary || p.summary_short || "";
        snippets.push(`Doc ${idx + 1}: ${title} — ${summary.slice(0, 200)}`);
      });
    } catch {
      /* ignore */
    }
    return snippets.length ? snippets.join("\n") : "";
  };

  const logToPipeline = async (text) => {
    if (!text) return;
    try {
      await callApi("/kitenga/gpt-whisper", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          whisper: text,
          session_id: sessionId,
          thread_id: threadId,
          use_retrieval: false,
          run_pipeline: true,
          save_vector: true,
          use_openai_summary: true,
          use_openai_translation: false,
          mode,
          allow_taonga_store: mode === "taonga",
          source: "ui-chat",
        }),
      });
    } catch {
      /* best-effort */
    }
  };

  const buildTranscript = () => {
    if (!responses.length) return "";
    const turns = [...responses].slice(0, 10).reverse(); // last 10 in chronological order
    return turns
      .map((entry) => {
        const promptText = (entry.prompt || "").slice(0, 400);
        const replyText = renderReplyText(entry.reply || {});
        return `User: ${promptText}\nAssistant: ${replyText ? replyText.slice(0, 400) : ""}`;
      })
      .join("\n\n");
  };

  useEffect(() => {
    const container = document.getElementById("chat-feed");
    if (container) {
      container.scrollTop = container.scrollHeight;
    }
  }, [responses]);

  const sendMessage = async ({ forcePipeline = false, forceSummary = false } = {}) => {
    setError("");
    if (!prompt.trim() && !file) {
      setError("Type something to send or attach a file.");
      return;
    }
    setBusy(true);
    try {
      const guidance = [
        "You are Kitenga Te Ao, a friendly kaitiaki. Respond with mana and clarity, keep taonga private when mode=taonga, and weave te reo naturally.",
        "When helpful, give a brief reasoning or steps before the final answer.",
      ];
      const ctx = await buildContext(prompt);
      const enhancedPrompt = `${guidance.join(" ")}\n\n${prompt}${ctx ? `\n\nContext:\n${ctx}` : ""}`;

      let reply;
      const preferAssistantRoute = !file && !forcePipeline && !forceSummary;
      if (file) {
        const form = new FormData();
        form.append("file", file, fileName || file.name || `upload_${uuidv4()}.txt`);
        form.append("whisper", enhancedPrompt || "");
        form.append("session_id", sessionId);
        form.append("thread_id", threadId || "");
        form.append("use_retrieval", "false"); // skip retrieval for uploads to avoid timeouts
        form.append("run_pipeline", forcePipeline ? "true" : "false"); // opt-in pipeline
        form.append("save_vector", "true");
        form.append("use_openai_summary", "true"); // ensure summary returned
        form.append("use_openai_translation", useTranslation ? "true" : "false");
        form.append("mode", mode);
        form.append("allow_taonga_store", mode === "taonga" ? "true" : "false");
        form.append("source", "ui-chat");
        reply = await callApi("/kitenga/gpt-whisper", {
          method: "POST",
          body: form,
          timeoutMs: 180000,
        });
      } else {
        if (preferAssistantRoute) {
          const payload = {
            prompt: enhancedPrompt,
            session_id: sessionId,
            thread_id: threadId,
            metadata: { mode, source: "ui-chat" },
          };
          const askResponse = await callApi("/kitenga/ask", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
          });
          reply = {
            response: askResponse?.reply,
            thread_id: askResponse?.thread_id,
            run_id: askResponse?.run_id,
            assistant_id: askResponse?.assistant_id,
            tool_results: askResponse?.tool_results || [],
            mode: "assistant",
            source: "kitenga_ask",
          };
        } else {
          const payload = {
            whisper: enhancedPrompt,
            session_id: sessionId,
            thread_id: threadId,
            use_retrieval: useRetrieval,
            run_pipeline: forcePipeline,
            save_vector: true,
            use_openai_summary: forceSummary || useSummary,
            use_openai_translation: useTranslation,
            mode,
            allow_taonga_store: mode === "taonga",
            source: "ui-chat",
          };
          reply = await callApi("/kitenga/gpt-whisper", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
          });
        }
      }
      if (reply?.thread_id) {
        setThreadId(reply.thread_id);
        localStorage.setItem("kaitiaki_thread_id", reply.thread_id);
      }
      const entry = {
        id: uuidv4(),
        prompt: prompt || fileName || "[file]",
        reply,
        kind: file ? "file" : forceSummary ? "summary" : "chat",
        ts: new Date().toISOString(),
      };
      setResponses((prev) => [entry, ...prev].slice(0, 15));
      setLastReply(entry);
      // keep prompt for convenience; clear file after send
      setFile(null);
      setFileName("");
    } catch (err) {
      setError(err.message || "Assistant call failed.");
    } finally {
      setBusy(false);
    }
  };

  const onSubmit = (event) => {
    if (event && event.preventDefault) event.preventDefault();
    return sendMessage();
  };

  const runSimpleAction = async (kind) => {
    setError("");
    const hasText = !!prompt.trim();
    const hasFile = !!file;
    if (!hasText && !hasFile && kind !== "sync" && kind !== "recall") {
      setError("Add text or attach a file first.");
      return;
    }
    setBusy(true);
    try {
      let result;
      const pushReply = (reply, kind) => {
        const entry = {
          id: uuidv4(),
          prompt: prompt || fileName || "[file]",
          reply,
          kind,
          ts: new Date().toISOString(),
        };
        setResponses((prev) => [entry, ...prev].slice(0, 15));
        setLastReply(entry);
      };
      if (kind === "translate") {
        result = await callApi("/reo/translate", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text: prompt }),
        });
        pushReply({ response: result.output, kind }, kind);
        logToPipeline(result.output || prompt);
      } else if (kind === "explain") {
        result = await callApi("/reo/explain", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text: prompt }),
        });
        pushReply({ response: result.output, kind }, kind);
        logToPipeline(result.output || prompt);
      } else if (kind === "pronounce") {
        result = await callApi("/reo/pronounce", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text: prompt }),
        });
        pushReply({ response: result.output, kind }, kind);
        logToPipeline(result.output || prompt);
      } else if (kind === "summarize") {
        await sendMessage({ forcePipeline: true, forceSummary: true });
      } else if (kind === "research") {
        result = await callApi("/research/stacked", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ query: prompt, limit: 5 }),
        });
        pushReply({ response: JSON.stringify(result, null, 2), kind }, kind);
      } else if (kind === "sync") {
        result = await callApi("/documents/profiles?limit=5");
        pushReply({ response: "Recent docs:\n" + JSON.stringify(result.profiles || [], null, 2), kind }, kind);
      } else if (kind === "recall") {
        const vector = await callApi("/vector/search", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ query: prompt, top_k: 5 }),
        });
        const recent = await callApi("/documents/profiles?limit=5");
        pushReply(
          {
            response:
              "Vector recall:\n" +
              JSON.stringify(vector?.matches || vector?.results || [], null, 2) +
              "\n\nRecent docs:\n" +
              JSON.stringify(recent?.profiles || [], null, 2),
          },
          kind
        );
      } else if (kind === "ocr") {
        if (!file) {
          setError("Attach an image first for OCR.");
        } else {
          const form = new FormData();
          form.append("file", file, fileName || file.name || `upload_${uuidv4()}.png`);
          const resp = await callApi("/intake/ocr", {
            method: "POST",
            body: form,
          });
          pushReply({ summary: resp?.summary || resp?.text_extracted || JSON.stringify(resp) }, kind);
          logToPipeline(resp?.summary || resp?.text_extracted);
          setFile(null);
          setFileName("");
        }
      } else if (kind === "save_chat") {
        const transcript = buildTranscript() || prompt;
        let pipelineResp = null;
        if (transcript) {
          pipelineResp = await callApi("/kitenga/gpt-whisper", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              whisper: transcript,
              session_id: sessionId,
              thread_id: threadId,
              use_retrieval: false,
              run_pipeline: true,
              save_vector: true,
              use_openai_summary: true,
              use_openai_translation: false,
              mode,
              allow_taonga_store: mode === "taonga",
              source: "ui-chat-save",
            }),
            timeoutMs: 180000,
          });
          if (pipelineResp?.thread_id) {
            setThreadId(pipelineResp.thread_id);
            localStorage.setItem("kaitiaki_thread_id", pipelineResp.thread_id);
          }
        }
        const saveResult = await callApi(`/chat/save-session?session_id=${encodeURIComponent(sessionId)}`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            title: prompt.slice(0, 60) || "UI chat session",
            tags: "",
            summarize: true,
            summary_words: SUMMARY_WORDS,
            write_ari: mode === "research",
          }),
        });
        pushReply({ ...saveResult, pipeline: pipelineResp }, kind);
        setPrompt("");
      } else if (kind === "web_search") {
        result = await callApi("/research/web_search", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ query: prompt, limit: 5, session_id: sessionId }),
        });
        pushReply({ response: JSON.stringify(result, null, 2), kind }, kind);
        logToPipeline(JSON.stringify(result, null, 2));
      }
    } catch (err) {
      setError(err.message || "Action failed.");
    } finally {
      setBusy(false);
    }
  };

  const collected = responses
    .map((r) => {
      const reply = r.reply || {};
      if (reply.summary) return reply.summary.slice(0, 120) + (reply.summary.length > 120 ? "…" : "");
      if (reply.summary_long) return reply.summary_long.slice(0, 120) + "…";
      const maybe = reply.response;
      if (!maybe) return null;
      try {
        const data = typeof maybe === "string" ? JSON.parse(maybe) : maybe;
        if (data?.results?.length) {
          const first = data.results[0];
          return first.title || first.url || "web result";
        }
        if (Array.isArray(data) && data.length) {
          const first = data[0];
          return first.title || first.source || "result";
        }
      } catch {
        return typeof maybe === "string" ? maybe.slice(0, 80) : null;
      }
      return null;
    })
    .filter(Boolean)
    .slice(0, 6);

  const renderEntry = (entry) => {
    const kind = entry.kind || "chat";
    const replyText = renderReplyText(entry.reply);
    const isChat = ["chat", "translate", "explain", "pronounce", "summarize", "research", "web_search"].includes(kind);
    const badges = [];
    if (entry.reply?.vector) badges.push("vector ✓");
    if (entry.reply?.pipeline) badges.push("pipeline ✓");
    if (entry.reply?.summary) badges.push("summary");
    if (entry.reply?.translation) badges.push("translation");
    if (entry.reply?.thread_id) badges.push(`thread ${entry.reply.thread_id}`);
    if (entry.reply?.source) badges.push(entry.reply.source);
    const toolResults = Array.isArray(entry.reply?.tool_results)
      ? entry.reply.tool_results.filter(Boolean)
      : [];
    const renderToolResult = (tool, idx) => {
      const label = tool?.tool || tool?.name || tool?.function?.name || `tool_${idx + 1}`;
      const status = (tool?.status || "ok").toString();
      const payload = tool?.result ?? tool?.output ?? tool?.reason ?? "";
      const textOutput = (() => {
        if (payload == null) return "";
        if (typeof payload === "string") return payload;
        try {
          return JSON.stringify(payload, null, 2);
        } catch {
          return String(payload);
        }
      })();
      return (
        <div key={idx} className="rounded-lg border border-border/60 bg-panel/70 px-3 py-2 text-xs text-koru1">
          <div className="flex flex-wrap gap-2 text-[11px] font-semibold text-primary">
            <span>{label}</span>
            <span className="uppercase tracking-wide text-koru2">{status}</span>
          </div>
          {textOutput && <pre className="mt-1 whitespace-pre-wrap break-words text-[11px] text-koru2">{textOutput}</pre>}
        </div>
      );
    };
    if (isChat) {
      return (
        <div key={entry.id} className="space-y-1">
          <ChatMessage role="user" content={entry.prompt} />
          <ChatMessage role="assistant" content={replyText} />
          {toolResults.length > 0 && <div className="space-y-2">{toolResults.map(renderToolResult)}</div>}
          {!!badges.length && (
            <div className="flex flex-wrap gap-2 text-[11px] text-koru2">
              {badges.map((b, idx) => (
                <span key={idx} className="px-2 py-1 rounded-full border border-border bg-panel/60">
                  {b}
                </span>
              ))}
            </div>
          )}
        </div>
      );
    }
    return (
      <ToolResultCard
        key={entry.id}
        title={kind}
        content={`${entry.prompt ? `User: ${entry.prompt}\n\n` : ""}${replyText || ""}`}
      />
    );
  };

  return (
    <KitengaShell>
      <div className={`h-full flex flex-col ${className}`}>
        <div className="border-b border-border bg-panel/60 px-6 py-3 flex flex-wrap items-center gap-2">
          <span className={`badge ${status?.openai_ok ? "badge-emerald" : "badge-rose"}`}>OpenAI {status?.openai_ok ? "ok" : "down"}</span>
          <span className={`badge ${status?.supabase_ok ? "badge-emerald" : "badge-rose"}`}>Supabase {status?.supabase_ok ? "ok" : "down"}</span>
          <span className="badge badge-slate">Vector {status?.vector_status ?? "n/a"}</span>
          <span className="badge badge-slate">API {baseUrl}</span>
          {collected.length > 0 && (
            <div className="flex flex-wrap gap-2 text-xs ml-auto">
              {collected.map((item, idx) => (
                <span key={idx} className="rounded-full bg-panel/60 border border-border px-3 py-1 text-koru2">
                  {item}
                </span>
              ))}
            </div>
          )}
        </div>

        <div className="flex flex-1 flex-col lg:flex-row gap-4 p-6">
          <div className="rounded-xl border border-[color:var(--color-border)/.3] bg-[color:var(--color-panel)/.85] backdrop-blur-md shadow-[0_0_16px_var(--color-border)/.15] p-4 space-y-2 w-full lg:w-80 h-full overflow-y-auto">
            <p className="text-sm font-semibold text-primary">Supabase recent</p>
            <p className="text-xs text-muted">Last 10 `tepo_files` entries (local time).</p>
            <div className="mt-2 space-y-2 h-full overflow-y-auto pr-1">
              {(profiles || []).slice(0, 10).map((p, idx) => {
                const ts = p.updated_at || p.created_at;
                const title = p.title || p.raw_path || p.clean_path || "Untitled";
                return (
                  <div key={idx} className="rounded-lg border border-[color:var(--color-border)/.3] bg-[color:var(--color-panel)/.85] backdrop-blur-md shadow-[0_0_16px_var(--color-border)/.15] p-2">
                    <p className="text-xs text-koru1">{title}</p>
                    {p.summary && <p className="text-[11px] text-koru2 mt-1 line-clamp-2">{p.summary}</p>}
                    <p className="text-[11px] text-koru2 mt-1">{ts ? new Date(ts).toLocaleString() : "—"}</p>
                  </div>
                );
              })}
              {!profiles?.length && <p className="text-xs text-muted">No recent profiles.</p>}
            </div>
          </div>

          <div className="flex-1 flex flex-col gap-4 overflow-hidden">
            <div id="chat-feed" className="flex-1 overflow-y-auto space-y-3 pr-1 scrollbar-thin">
              {responses.length === 0 && (
                <div className="rounded-xl border border-[color:var(--color-border)/.3] bg-[color:var(--color-panel)/.85] backdrop-blur-md shadow-[0_0_16px_var(--color-border)/.15] p-4 text-koru2 text-sm">
                  Start typing or choose an action to see replies here. Web search, research, and pipeline runs will stack into this stream.
                </div>
              )}
              {[...responses].reverse().map((entry) => renderEntry(entry))}
            </div>

            <div className="rounded-xl border border-[color:var(--color-border)/.3] bg-[color:var(--color-panel)/.85] backdrop-blur-md shadow-[0_0_16px_var(--color-border)/.15] p-4 space-y-3 shrink-0">
              <textarea
                className="min-h-[180px] w-full rounded-xl border border-border bg-panel/60 p-4 text-koru1 text-lg placeholder:text-koru2 focus:outline-none focus:ring-2 focus:ring-koru1"
                placeholder="Ask, drop a PDF, request summary, translation, or retrieval…"
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    onSubmit();
                  }
                }}
                disabled={busy}
              />

              <div className="flex flex-wrap items-center gap-3 rounded-xl border border-border bg-panel/60 p-3">
                <label className="text-xs text-koru2">
                  <span className="mr-2 text-koru1 font-semibold">File:</span>
                  <input
                    type="file"
                    className="text-xs text-koru1"
                    onChange={(e) => {
                      const f = e.target.files?.[0];
                      setFile(f || null);
                      setFileName(f?.name || "");
                    }}
                    disabled={busy}
                  />
                </label>

                <div className="flex items-center gap-2 text-sm text-koru1">
                  <label className="flex items-center gap-1">
                    <input type="radio" name="mode" checked={mode === "research"} onChange={() => setMode("research")} />
                    Research
                  </label>
                  <label className="flex items-center gap-1">
                    <input type="radio" name="mode" checked={mode === "taonga"} onChange={() => setMode("taonga")} />
                    Taonga
                  </label>
                </div>

                <button
                  type="button"
                  onClick={onSubmit}
                  className="ml-auto px-4 py-1 rounded-full bg-[color:var(--color-panel)] border border-[color:var(--color-border)/.3] hover:bg-[color:var(--color-border)/.2] hover:text-[color:var(--color-glow)] shadow transition-all glow text-sm font-semibold disabled:opacity-60"
                  disabled={busy}
                >
                  {busy ? "Sending..." : "Send"}
                </button>
                {busy && <Spinner />}
                {error && <p className="text-sm text-rose-300">{error}</p>}
              </div>

              <div className="flex flex-wrap gap-2">
                {[
                  { key: "summarize", label: "Summarize", tone: "bg-primary/20 text-primary" },
                  { key: "translate", label: "Translate", tone: "bg-panel/60 text-koru1" },
                  { key: "explain", label: "Explain", tone: "bg-panel/60 text-koru1" },
                  { key: "pronounce", label: "Pronounce", tone: "bg-panel/60 text-koru1" },
                  { key: "ocr", label: "OCR (image)", tone: "bg-panel/60 text-koru1" },
                  { key: "research", label: "Research", tone: "bg-panel/60 text-koru1" },
                  { key: "web_search", label: "Web Search", tone: "bg-panel/60 text-koru1" },
                  { key: "sync", label: "Sync (Supabase)", tone: "bg-panel/60 text-koru1" },
                  { key: "recall", label: "Recall (vectors)", tone: "bg-panel/60 text-koru1" },
                  { key: "save_chat", label: "Save chat", tone: "bg-panel/60 text-koru1" },
                ].map((btn) => (
                  <button
                    key={btn.key}
                    className={`px-4 py-1 rounded-full bg-[color:var(--color-panel)] border border-[color:var(--color-border)/.3] hover:bg-[color:var(--color-border)/.2] hover:text-[color:var(--color-glow)] shadow transition-all text-xs ${btn.tone}`}
                    onClick={() => runSimpleAction(btn.key)}
                    disabled={busy}
                  >
                    {btn.label}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </KitengaShell>
  );
}
