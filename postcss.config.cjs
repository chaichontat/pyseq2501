const tailwindcss = require("tailwindcss");
const autoprefixer = require("autoprefixer");
const cssnano = require("cssnano");

const mode = process.env.NODE_ENV;
const dev = mode === "development";

const config = {
  plugins: {
    //Some plugins, like tailwindcss/nesting, need to run before Tailwind,
    "postcss-import": {},
    "tailwindcss/nesting": {},
    tailwindcss: {},
    //But others, like autoprefixer, need to run after,
    autoprefixer: {},
    cssnano: { preset: "default" },
  },
};

module.exports = config;
