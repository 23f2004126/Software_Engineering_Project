/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Primary colors
        'primary': '#10B981',        // emerald-500
        'primary-dark': '#059669',   // emerald-700
        'primary-light': '#D1FAE5',  // emerald-100
        
        // Accent and status colors
        'accent': '#F59E0B',         // amber-500
        'danger': '#EF4444',         // red-500
        
        // Surface and background
        'surface': '#FFFFFF',        // white
        'base': '#F8FAFC',           // slate-50
        
        // Text colors
        'text-primary': '#0F172A',   // slate-900
        'text-muted': '#64748B',     // slate-500
        
        // Border
        'border-light': '#E2E8F0',   // slate-200
      },
      fontFamily: {
        'sans': ['DM Sans', 'sans-serif'],
        'mono': ['DM Mono', 'monospace'],
      },
    },
  },
  plugins: [],
}


