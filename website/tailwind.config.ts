import type { Config } from "tailwindcss";
import typography from "@tailwindcss/typography";

export default {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#EEF5FB",
          100: "#D9EAF7",
          200: "#B8D6EF",
          300: "#90BDE4",
          400: "#5E9FD6",
          500: "#377FBE",
          600: "#2B679B",
          700: "#254F78",
          800: "#243D5F",
          900: "#22314E"
        },
        cta: {
          500: "#39D95D",
          600: "#29BB48"
        },
        flow: {
          100: "#FFE3D3",
          400: "#F08A45",
          500: "#E9762B"
        }
      },
      fontFamily: {
        heading: ["Baloo 2", "ui-sans-serif", "system-ui", "sans-serif"],
        sans: ["DM Sans", "ui-sans-serif", "system-ui", "sans-serif"],
        mono: [
          "ui-monospace",
          "SFMono-Regular",
          "Menlo",
          "Monaco",
          "Consolas",
          "Liberation Mono",
          "Courier New",
          "monospace"
        ]
      }
    }
  },
  plugins: [typography]
} satisfies Config;
