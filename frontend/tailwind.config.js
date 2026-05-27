/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ['"DM Sans"', "sans-serif"],
        mono: ['"Geist Mono"', "monospace"],
        display: ['"Plus Jakarta Sans"', "sans-serif"],
      },
      colors: {
        surface: {
          base: "#0a0c10",
          raised: "#111318",
          card: "#181c24",
          border: "#252a35",
        },
        accent: {
          DEFAULT: "#8B5CF6",
          dim: "#7C3AED",
          glow: "rgba(139,92,246,0.18)",
        },
        text: {
          primary: "#e8eaf0",
          secondary: "#8b91a0",
          muted: "#4e5565",
        },
        score: {
          high: "#4ADE80",
          mid: "#cfff04",
          low: "#FB7185",
        },
      },
    },
  },
  plugins: [],
};
