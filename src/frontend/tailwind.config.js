/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{js,ts,jsx,tsx,mdx}'],
  theme: {
    extend: {
      colors:{
        alanturing:{
          100: '#62c8f2',
          400: '#4aa4dc',
          800: '#206ab2'
        }
      }
    },
  },
  plugins: [],
};
