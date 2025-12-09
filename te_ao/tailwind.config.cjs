/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        koru: {
          night: "#020617",
          fern: "#064e3b",
          tide: "#0f172a",
          mist: "#94a3b8",
        },
        night: "#020617",
        fade: "#0f172a",
        light: "#e2e8f0",
        accent: "#6ee7b7",
        "koru-deep": "#020617",
        "koru-teal": "#6ee7b7",
        "koru-mist": "#94a3b8",
        "koru-white": "#e2e8f0",
        awa: {
          bg: "var(--bg)",
          panel: "var(--panel-bg)",
          text: "var(--text)",
          border: "var(--border)",
          accent: "var(--accent)",
        },
        back: "#020617",
        panel: "#0f172a",
        border: "#1e293b",
        koru1: "#e2e8f0",
        koru2: "#94a3b8",
        koru3: "#020617",
      },
      fontFamily: {
        ui: ["Inter", "sans-serif"],
      },
    },
  },
  plugins: [],
};
