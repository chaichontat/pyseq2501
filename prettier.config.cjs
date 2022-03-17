module.exports = {
  plugins: [require("prettier-plugin-tailwindcss")], // Tailwind bundles Svelte.
  tailwindConfig: "tailwind.config.cjs",

  printWidth: 150,
  useTabs: false,
  htmlWhitespaceSensitivity: "ignore",
  overrides: [
    {
      files: "*.svelte",
      options: {
        printWidth: 200,
      },
    },
  ],
};
