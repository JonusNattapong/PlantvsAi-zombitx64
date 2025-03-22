/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./templates/**/*.{html,js,ts}"],
  theme: {
    extend: {
      fontFamily: {
        kanit: ['Kanit', 'sans-serif'],
      },
      colors: {
        primary: {
          DEFAULT: '#ff4e50',
          hover: '#f9d423',
        },
        dark: {
          DEFAULT: '#1a1a2e',
          secondary: '#16213e',
        },
      },
    },
  },
  plugins: [],
} 