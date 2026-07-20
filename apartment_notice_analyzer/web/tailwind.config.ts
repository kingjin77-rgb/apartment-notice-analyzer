import type { Config } from "tailwindcss";

// 디자인 토큰 출처: DESIGN-notion.md (Notion 디자인 언어 분석)
const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        primary: "#0075de",
        "primary-active": "#005bab",
        secondary: "#213183",
        canvas: "#ffffff",
        "canvas-soft": "#f6f5f4",
        ink: "#000000",
        "ink-secondary": "#31302e",
        "ink-muted": "#615d59",
        "ink-faint": "#a39e98",
        hairline: "#e6e6e6",
        "accent-sky": "#62aef0",
        "accent-purple": "#d6b6f6",
        "accent-pink": "#ff64c8",
        "accent-orange": "#dd5b00",
        "accent-teal": "#2a9d99",
        "accent-green": "#1aae39",
      },
      fontFamily: {
        sans: [
          "Inter",
          "-apple-system",
          "system-ui",
          "Segoe UI",
          "Helvetica",
          "Arial",
          "sans-serif",
        ],
      },
      borderRadius: {
        xs: "4px",
        sm: "5px",
        md: "8px",
        lg: "12px",
        xl: "16px",
      },
      boxShadow: {
        soft: "0 0.175px 1.041px rgba(0,0,0,0.01), 0 0.8px 2.925px rgba(0,0,0,0.02), 0 2.025px 7.847px rgba(0,0,0,0.027), 0 4px 18px rgba(0,0,0,0.04)",
        elevated: "0 23px 52px rgba(0,0,0,0.05)",
      },
      letterSpacing: {
        display: "-2.125px",
        heading1: "-1px",
        heading2: "-0.625px",
      },
    },
  },
  plugins: [],
};
export default config;
