const items = ["🏠", "🔍", "📖", "📂", "⚙️"];

export default function Sidebar({ className = "" }) {
  return (
    <div className={`flex flex-col items-center space-y-6 ${className}`}>
      {items.map((icon, i) => (
        <button key={i} className="text-koru1 hover:text-koru2 transition text-xl" aria-label={`nav-${i}`}>
          {icon}
        </button>
      ))}
    </div>
  );
}
