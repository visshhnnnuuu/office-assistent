/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['var(--font-noto-sans)', 'system-ui', 'sans-serif'],
        deva: ['var(--font-noto-deva)', 'sans-serif'],
        mlym: ['var(--font-noto-mlym)', 'sans-serif'],
      },
      colors: {
        claude: {
          bg: '#FBF9F5',
          sidebar: '#F3EFEA',
          card: '#FFFFFF',
          border: '#E8E2D9',
          borderDark: '#D4CBBF',
          text: '#222222',
          muted: '#6B655B',
          accent: '#C96442', // Terracotta / warm rust accent
          accentHover: '#B25435',
          highlight: '#F3ECE3',
        }
      }
    },
  },
  plugins: [],
}
