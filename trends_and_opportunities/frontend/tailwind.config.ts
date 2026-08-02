import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#12131A",
        panel: "#191B24",
        line: "#2A2D3A",
        signal: "#5CE1B0",
        warn: "#F2A93B",
        danger: "#E85D5D",
        muted: "#8A8DA3",
        paper: "#EDEEF3",
      },
      fontFamily: {
        display: ["'Space Grotesk'", "sans-serif"],
        body: ["'IBM Plex Sans'", "sans-serif"],
        mono: ["'IBM Plex Mono'", "monospace"],
      },
    },
  },
  plugins: [],
} satisfies Config;
