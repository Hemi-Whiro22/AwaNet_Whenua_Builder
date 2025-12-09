import koruMark from "../../assets/koru.svg";

export default function HeaderBar() {
  return (
    <div className="flex items-center justify-between px-6 py-3 border-b border-[color:var(--color-border)/.4] bg-[color:var(--color-bg)]">
      <div className="flex items-center space-x-3">
        <img src={koruMark} className="h-7 w-7 opacity-90" />
        <h1 className="text-xl font-bold tracking-wide">Kitenga Whiro — Kaitiaki</h1>
      </div>
      <span className="text-[color:var(--color-text-secondary)] italic">“He waka eke noa”</span>
    </div>
  );
}
