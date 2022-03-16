module.exports = {
  parser: "@typescript-eslint/parser", // add the TypeScript parser
  plugins: [
    "svelte3",
    "@typescript-eslint", // add the TypeScript plugin
  ],
  extends: ["eslint:recommended", "plugin:@typescript-eslint/recommended"],
  overrides: [
    // this stays the same
    {
      files: ["*.svelte"],
      processor: "svelte3/svelte3",
    },
  ],
  settings: {
    "svelte3/typescript": true, // load TypeScript as peer dependency
    // ...
  },
};
