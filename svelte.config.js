import adapter from "@sveltejs/adapter-static";
import path from "path";
import preprocess from "svelte-preprocess";

const ci = process.env.CI === "true";

/** @type {import('@sveltejs/kit').Config} */
const config = {
  // Consult https://github.com/sveltejs/svelte-preprocess
  // for more information about preprocessors
  preprocess: [
    preprocess({
      postcss: true,
    }),
  ],

  kit: {
    vite: {
      resolve: {
        alias: {
          $src: path.resolve("./src"),
          $comps: path.resolve("./src/components"),
        },
      },
      optimizeDeps: {
        include: ["fast-deep-equal", "clone", "semver", "json-stringify-pretty-compact", "fast-json-stable-stringify"],
      },
    },
    paths: {
      base: ci ? "/pyseq2501-web" : "",
    },
    appDir: "internal",
    adapter: adapter({
      // default options are shown
      pages: "build",
      assets: "build",
      fallback: null,
    }),
    prerender: { default: true },
  },
};

export default config;
