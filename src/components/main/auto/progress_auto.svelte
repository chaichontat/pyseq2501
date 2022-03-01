<script lang="ts">
  import { cmdStore, statusStore as ss } from "$src/stores/store";
  import tooltip from "$src/tooltip";
  import type { Tweened } from "svelte/motion";
  import Progress from "../progress.svelte";

  let step: [number, number, number] = [0, 0, 0];
  let progress: Tweened<number>;
  // export let stats: { height: number; width: number; n_cols: number; n_bundles: number; n_z: number; time: number };
  export let fc_ = 0;

  $: {
    if ($cmdStore?.step) {
      step = $cmdStore.step;
      // progress.set((step[2] * (stats.n_z * stats.n_bundles) + step[1] * stats.n_bundles + step[0]) / (stats.n_bundles * stats.n_cols * stats.n_z));
    }
  }

  let captureState: "ok" | "gray" | "stop" = "ok";
  let previewState: "ok" | "gray" | "stop" = "ok";
  let interval: ReturnType<typeof setInterval> | undefined;
  let t: number = 0;

  $: captureState = $ss.block === "capturing" ? "stop" : "ok";
  $: previewState = $ss.block === "previewing" ? "stop" : "ok";

  $: if (!$ss.block && interval) clearInterval(interval);

  function handleCapture() {
    console.log("hi");
    if (interval) clearInterval(interval);
    if ($ss.block === "capturing") {
      $cmdStore = { cmd: "stop" };
    } else {
      t = 0;
      interval = setInterval(() => {
        t += 1;
      }, 1000);
      $cmdStore = { cmd: "capture" };
      $ss.block = "capturing";
    }
  }

  function handlePreview() {
    if (interval) clearInterval(interval);
    if ($ss.block === "previewing") {
      $cmdStore = { cmd: "stop" };
    } else {
      t = 0;
      interval = setInterval(() => {
        t += 1;
      }, 1000);
      $cmdStore = { cmd: "preview" };
      $ss.block = "previewing";
    }
  }
</script>

<Progress {progress}>
  <div slot="buttons" class="grid grid-flow-row w-36">
    <button
      type="button"
      class="text-lg text-white focus:ring-4 shadow-lg font-medium rounded-lg px-5 py-2.5 text-center mr-2 mb-2"
      class:focus:ring-indigo-300={captureState === "ok"}
      class:focus:ring-orange-300={captureState === "stop"}
      class:start={captureState === "ok"}
      class:stop={captureState === "stop"}
      on:click={handleCapture}
      disabled={captureState !== "ok"}
    >
      <div class="flex items-center h-12 text-lg">
        {#if $ss.block === "capturing" || $ss.block === "previewing"}
          <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 10a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z" />
          </svg>
          <p class="flex-grow">Stop</p>
        {:else}
          <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6 -ml-0.5 mr-1 -translate-y-[0.25px]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          Start
        {/if}
      </div>
    </button>

    <button
      type="button"
      id="preview"
      class="text-lg mt-2 text-white focus:ring-4 focus:ring-violet-300 font-medium rounded-lg shadow px-4 py-2.5 text-center inline-flex items-center mr-2"
      disabled={Boolean($ss.block)}
      use:tooltip={"Take a 16-bundle image based on the current position without saving."}
      on:click={handlePreview}
    >
      <div class="flex items-center">
        <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
        Validate
      </div>
    </button>
  </div>

  <div class="grid max-w-4xl grid-cols-4 mt-1">
    <!-- N Bundles -->
    <section class="flex flex-col gap-y-1">
      <div class="flex items-center">
        <span class="text-4xl font-bold">
          <span class="font-mono">{step[0]}</span>
          /
          <span class="w-32 px-2 font-mono text-4xl font-bold ">{1}</span>
        </span>
      </div>
      Steps
    </section>

    <section class="flex flex-col gap-y-1">
      <div class="flex items-center">
        <span class="text-4xl font-bold">
          <span class="font-mono">{step[1]}</span>
          /
          <span class="w-32 px-2 font-mono text-4xl font-bold ">{2}</span>
        </span>
      </div>
      Z-steps taken
    </section>

    <section class="flex flex-col gap-y-1">
      <div class="flex items-center">
        <span class="text-4xl font-bold">
          <span class="font-mono">{step[2]}</span>
          /
          <span class="w-32 px-2 font-mono text-4xl font-bold ">{4}</span>
        </span>
      </div>
      Columns taken
    </section>

    <section class="flex flex-col">
      <span class="text-lg font-medium">Elapsed time: {t} s</span>
      <span class="text-lg font-medium">Total time: {5 / 10} s</span>
    </section>
  </div>
</Progress>

<style lang="postcss">
  .start {
    @apply transition-all bg-gradient-to-r from-indigo-500 to-indigo-700 shadow-indigo-500/50 hover:from-indigo-600 hover:to-indigo-800 focus:ring-4 focus:ring-indigo-300 active:from-indigo-700;
  }

  .stop {
    @apply transition-all bg-gradient-to-r from-orange-500 to-orange-700 shadow-orange-500/50 hover:from-orange-600 hover:to-orange-800 active:from-orange-700 focus:ring-orange-300;
  }

  #preview {
    @apply transition-all bg-gradient-to-r from-violet-400 to-violet-600 shadow-violet-500/50 hover:from-violet-500 hover:to-violet-700 active:from-violet-600 disabled:text-gray-400 disabled:from-gray-50 disabled:via-gray-100 disabled:to-gray-200 disabled:shadow-gray-400/50;
  }
</style>
