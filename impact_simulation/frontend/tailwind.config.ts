import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#12131A",       // near-black canvas
        panel: "#191B24",     // card surface
        line: "#2A2D3A",      // hairline borders
        signal: "#5CE1B0",    // "improving" accent — instrument-panel green
        warn: "#F2A93B",      // "volatile" amber
        danger: "#E85D5D",    // "declining" red
        muted: "#8A8DA3",     // secondary text
        paper: "#EDEEF3",     // primary text on dark
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
