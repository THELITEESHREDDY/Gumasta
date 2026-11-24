/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: "class",
  content: [
    "./app/**/*.{js,jsx,ts,tsx}",
    "./src/**/*.{js,jsx,ts,tsx}",
    "./components/**/*.{js,jsx,ts,tsx}",
  ],
  presets: [require("nativewind/preset")],
  theme: {
    extend: {
      colors: {
        primary: "#166534",
        background: "#F9FAFB",
        surface: "#FFFFFF",
        success: "#16A34A",
        danger: "#DC2626",
      },
    },
  },
  plugins: [],
};