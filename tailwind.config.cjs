const defaultTheme = require('tailwindcss/defaultTheme')
const config = {
  mode: "jit",
  content: ["./src/**/*.{html,js,svelte,ts}"],

  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter var', ...defaultTheme.fontFamily.sans],
      },
    },
  },

  plugins: [require("daisyui"), require('@tailwindcss/forms')]
}

module.exports = config
