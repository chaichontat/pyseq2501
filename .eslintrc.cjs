module.exports = {
  env: {
    browser: true,
    es2021: true,
    node: true,
  },
  ignorePatterns: ["node_modules", "htmlcov", "build", "dist", ".svelte-kit", "*.cjs", "svelte.config.js"],
  parser: "@typescript-eslint/parser", // add the TypeScript parser
  plugins: [
    "svelte3",
    "@typescript-eslint", // add the TypeScript plugin
  ],
  parserOptions: {
    ecmaVersion: "es2021",
    sourceType: "module",
    tsconfigRootDir: __dirname,
    project: ["./tsconfig.json"],
  },
  extends: ["eslint:recommended", "plugin:@typescript-eslint/recommended", "plugin:@typescript-eslint/recommended-requiring-type-checking"],
  overrides: [
    // this stays the same
    {
      files: ["*.svelte"],
      processor: "svelte3/svelte3",
    },
  ],
  settings: {
    "svelte3/typescript": true, // load TypeScript as peer dependency
  },
};
