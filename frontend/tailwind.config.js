/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        navy: {
          DEFAULT: '#1a2e5a',
          light: '#244080',
          dark: '#142244',
        },
        info: '#dbeafe',
        alert: '#ea580c',
        success: '#15803d',
        danger: '#dc2626',
        surface: '#f3f4f6',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'ui-monospace', 'SFMono-Regular', 'Menlo', 'monospace'],
      },
      spacing: {
        navbar: '60px',
        sidebar: '240px',
      },
      minHeight: {
        touch: '44px',
        screen: '100vh',
      },
      minWidth: {
        touch: '44px',
      },
      boxShadow: {
        card: '0 1px 3px 0 rgb(0 0 0 / 0.08), 0 1px 2px -1px rgb(0 0 0 / 0.08)',
        panel: '0 4px 12px -2px rgb(0 0 0 / 0.10)',
      },
    },
  },
  plugins: [],
};
