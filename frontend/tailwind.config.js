// frontend/tailwind.config.js
/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    './app/**/*.{js,jsx,ts,tsx}',
    './components/**/*.{js,jsx,ts,tsx}',
    './lib/**/*.{js,jsx,ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: '#807853',
        secondary: '#312100ad',
        lightbg: '#ffffff',
        darkbg: '#312100ad',
      },
    },
  },
  plugins: [],
};
