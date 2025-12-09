export function Card({ className = "", children }) {
  return <div className={`rounded-xl border border-border bg-panel/60 ${className}`}>{children}</div>;
}

export function CardHeader({ className = "", children }) {
  return <div className={`px-4 pt-4 text-sm font-semibold ${className}`}>{children}</div>;
}

export function CardContent({ className = "", children }) {
  return <div className={`px-4 pb-4 text-sm ${className}`}>{children}</div>;
}
