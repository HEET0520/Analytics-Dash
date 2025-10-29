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
        primary: '#0ea5e9', // sky-500
        secondary: '#0b1220', // deep slate
        surface: '#0f172a', // slate-900
        muted: '#94a3b8', // slate-400
        brandStart: '#22d3ee', // cyan-400
        brandMid: '#60a5fa', // blue-400
        brandEnd: '#a78bfa', // violet-400
        lightbg: '#ffffff',
        darkbg: '#0b1220',
      },
      keyframes: {
        shimmer: {
          '0%': { backgroundPosition: '-700px 0' },
          '100%': { backgroundPosition: '700px 0' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-4px)' },
        },
        in: {
          '0%': { opacity: 0, transform: 'translateY(8px) scale(.98)' },
          '100%': { opacity: 1, transform: 'translateY(0) scale(1)' },
        },
      },
      animation: {
        shimmer: 'shimmer 1.6s infinite linear',
        float: 'float 6s ease-in-out infinite',
        in: 'in .35s ease-out both',
      },
      boxShadow: {
        glow: '0 10px 30px -10px rgba(34,211,238,.35)',
      },
      fontFamily: {
        // filled via next/font to ensure matching stack
        display: ['var(--font-display)', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        sans: ['var(--font-sans)', 'ui-sans-serif', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
};
