export default function ChatInput({ value, onChange, onSubmit, busy }) {
  return (
    <div className="flex items-center space-x-2">
      <input
        className="flex-1 bg-panel/60 rounded-lg border border-border px-3 py-2 text-koru1 placeholder:text-koru2 focus:outline-none focus:ring-2 focus:ring-koru1"
        placeholder="Type your message…"
        value={value}
        onChange={onChange}
        onKeyDown={(e) => {
          if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            onSubmit();
          }
        }}
        disabled={busy}
      />
      <button
        className="bg-panel/60 border border-koru1 text-koru1 hover:bg-koru2 hover:text-white rounded-lg px-3 py-2 text-sm font-semibold transition disabled:opacity-60 glow"
        onClick={onSubmit}
        disabled={busy}
      >
        Send
      </button>
    </div>
  );
}
