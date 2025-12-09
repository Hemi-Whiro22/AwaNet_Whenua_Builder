export function Button({ className = "", children, ...props }) {
  return (
    <button
      className={`rounded-lg px-3 py-2 font-semibold transition focus:outline-none focus:ring-2 focus:ring-primary ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}
