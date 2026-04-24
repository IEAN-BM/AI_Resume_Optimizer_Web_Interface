/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        navy: {
          50: "#f0f4ff",
          100: "#e0e9ff",
          200: "#c7d6fe",
          300: "#a5b8fc",
          400: "#8193f8",
          500: "#6270f1",
          600: "#4f52e5",
          700: "#3d3fca",
          800: "#2C3E7A",  // ← our accent from the PDF
          900: "#1e2a5e",
          950: "#141a3d",
        },
      },
    },
  },
  plugins: [],
}