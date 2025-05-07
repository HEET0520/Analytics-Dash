/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
      './pages/**/*.{js,ts,jsx,tsx,mdx}',
      './components/**/*.{js,ts,jsx,tsx,mdx}',
      './app/**/*.{js,ts,jsx,tsx,mdx}',
    ],
    theme: {
      extend: {
        colors: {
          'dark-bg': '#1a1f36',
          'card-bg': '#252a41',
          'primary-blue': '#6366f1',
          'text-gray': '#a0a5bd',
        },
      },
    },
    plugins: [],
  }