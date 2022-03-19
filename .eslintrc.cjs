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
    extraFileExtensions: [".svelte"],
    project: ["./tsconfig.json"],
  },
  extends: ["eslint:recommended", "plugin:@typescript-eslint/recommended", "plugin:@typescript-eslint/recommended-requiring-type-checking"],
  overrides: [
    // this stays the same
    {
      files: ["*.svelte"],
      processor: "svelte3/svelte3",
      rules: {
        "@typescript-eslint/restrict-template-expressions": "off",
        "@typescript-eslint/no-unsafe-argument": "off",
        "@typescript-eslint/no-unsafe-assignment": "off",
        "@typescript-eslint/no-unsafe-member-access": "off",
        "@typescript-eslint/no-unsafe-return": "off",
      },
    },
  ],
  settings: {
    "svelte3/typescript": true, // load TypeScript as peer dependency
  },
};
