import nextCoreWebVitals from "eslint-config-next/core-web-vitals";

const config = [
  {
    ignores: ["node_modules/**", ".next/**", "out/**"]
  },
  ...nextCoreWebVitals,
  {
    files: ["src/components/markdown.tsx"],
    rules: {
      "@next/next/no-img-element": "off"
    }
  }
];

export default config;
