/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        kotuku: "#E6F2F1",
        kowhai: "#f1c40f",
        night: "#0e1111",
        stone: "#1b1e1f",
        awa: "#00b894",
      },
    },
  },
  plugins: [],
};
