/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ['"DM Sans"', "sans-serif"],
        mono: ['"JetBrains Mono"', "monospace"],
        display: ['"Syne"', "sans-serif"],
      },
      colors: {
        surface: {
          base: "#0a0c10",
          raised: "#111318",
          card: "#181c24",
          border: "#252a35",
        },
        accent: {
          DEFAULT: "#f5a623",
          dim: "#c47d0e",
          glow: "rgba(245,166,35,0.15)",
        },
        text: {
          primary: "#e8eaf0",
          secondary: "#8b91a0",
          muted: "#4e5565",
        },
        score: {
          high: "#34d399",
          mid: "#fbbf24",
          low: "#f87171",
        },
      },
    },
  },
  plugins: [],
};
