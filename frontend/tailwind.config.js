/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  darkMode: ["class", '[data-theme="dark"]'],
  theme: {
    extend: {
      colors: {
        bg: {
          page: "var(--bg-page)",
          alt: "var(--bg-alt)",
          subtle: "var(--bg-subtle)",
        },
        text: {
          primary: "var(--text-primary)",
          secondary: "var(--text-secondary)",
          muted: "var(--text-muted)",
        },
        border: {
          subtle: "var(--border-subtle)",
          standard: "var(--border-standard)",
          prominent: "var(--border-prominent)",
        },
        brand: {
          green: "#3ecf8e",
          link: "var(--brand-link)",
          button: "var(--brand-button)",
          "button-hover": "var(--brand-button-hover)",
          accent: "var(--brand-accent)",
        },
        status: {
          tinggi: "var(--status-tinggi)",
          sedang: "var(--status-sedang)",
          rendah: "var(--status-rendah)",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["'JetBrains Mono'", "ui-monospace", "monospace"],
      },
      boxShadow: {
        "level-1": "var(--shadow-1)",
        "level-2": "var(--shadow-2)",
        "level-3": "var(--shadow-3)",
      },
      borderRadius: {
        pill: "9999px",
      },
    },
  },
  plugins: [],
};
