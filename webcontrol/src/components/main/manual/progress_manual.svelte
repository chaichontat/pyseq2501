<script lang="ts">
  import { cmdStore, localStore, statusStore as ss } from "$src/stores/store";
  import tooltip from "$src/tooltip";
  import { createEventDispatcher } from "svelte";
  import type { Tweened } from "svelte/motion";
  import Progress from "../progress.svelte";

  let step: [number, number, number] = [0, 0, 0];
  let progress: Tweened<number>;
  export let stats: { height: number; width: number; n_cols: number; n_bundles: number; n_z: number; time: number };

  const dispatch = createEventDispatcher();

  export function resetProgress() {
    step = [0, 0, 0];
    progress.set(0).catch(console.error);
  }

  $: {
    if (progress && $cmdStore?.step) {
      step = $cmdStore.step;
      const percent = (step[2] * (stats.n_z * stats.n_bundles) + step[1] * stats.n_bundles + step[0]) / (stats.n_bundles * stats.n_cols * stats.n_z);
      if (percent) progress.set(percent > 1 ? 1 : percent).catch(console.error);
    }
  }

  let captureState: "ok" | "gray" | "stop" = "ok";
  let previewState: "ok" | "gray" | "stop" = "ok";
  let interval: ReturnType<typeof setInterval> | undefined;
  let t = 0;

  $: captureState = $ss.block === "capturing" ? "stop" : "ok";
  $: previewState = $ss.block === "previewing" ? "stop" : "ok";

  $: if (!$ss.block && interval) clearInterval(interval);

  function handleCapture() {
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
      resetProgress();
    }
  }
</script>

<Progress bind:progress>
  <div slot="buttons" class="grid w-40 grid-flow-row">
    <button
      type="button"
      class="mr-2 mb-2 rounded-lg px-5 py-2.5 text-center text-lg font-medium text-white shadow-lg focus:ring-4"
      class:focus:ring-blue-300={captureState === "ok"}
      class:focus:ring-orange-300={captureState === "stop"}
      class:start={captureState === "ok"}
      class:stop={captureState === "stop"}
      use:tooltip={"Take image and save."}
      on:click={handleCapture}
      disabled={captureState !== "ok" || !$localStore.connected}
    >
      <div class="flex h-12 cursor-pointer items-center text-lg">
        {#if $ss.block === "capturing" || $ss.block === "previewing"}
          <svg xmlns="http://www.w3.org/2000/svg" class="mr-1 h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 10a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z" />
          </svg>
          <p class="flex-grow">Stop</p>
        {:else}
          <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6 -ml-0.5 mr-1 -translate-y-[0.25px]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          Capture
        {/if}
      </div>
    </button>

    <button
      type="button"
      id="preview"
      class="mt-2 mr-2 inline-flex items-center rounded-lg px-4 py-2.5 text-center text-lg font-medium text-white shadow focus:ring-4 focus:ring-sky-300"
      disabled={Boolean($ss.block) || !$localStore.connected}
      use:tooltip={"See the autofocus pane."}
      on:click={() => dispatch("autofocus")}
    >
      <div class="flex items-center">
        <svg xmlns="http://www.w3.org/2000/svg" class="mr-1 h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
        Autofocus
      </div>
    </button>
  </div>

  <div class="mt-1 grid max-w-4xl grid-cols-4">
    <!-- N Bundles -->
    <section class="flex flex-col gap-y-1">
      <div class="flex items-center">
        <span class="text-4xl font-bold">
          <span class="font-mono">{step[0]}</span>
          /
          <span class="w-32 px-2 font-mono text-4xl font-bold ">{stats.n_bundles}</span>
        </span>
      </div>
      Bundles taken
    </section>

    <section class="flex flex-col gap-y-1">
      <div class="flex items-center">
        <span class="text-4xl font-bold">
          <span class="font-mono">{step[1]}</span>
          /
          <span class="w-32 px-2 font-mono text-4xl font-bold ">{stats.n_z}</span>
        </span>
      </div>
      Z-steps taken
    </section>

    <section class="flex flex-col gap-y-1">
      <div class="flex items-center">
        <span class="text-4xl font-bold">
          <span class="font-mono">{step[2]}</span>
          /
          <span class="w-32 px-2 font-mono text-4xl font-bold ">{stats.n_cols}</span>
        </span>
      </div>
      Columns taken
    </section>

    <section class="flex flex-col">
      <span class="text-lg font-medium">Elapsed time: {t} s</span>
      <span class="text-lg font-medium">Total time: {(stats.n_bundles * stats.n_cols) / 10} s</span>
    </section>
  </div>
</Progress>

<style lang="postcss">
  .start {
    @apply bg-gradient-to-r from-blue-500 to-blue-700 shadow-blue-500/50 transition-all hover:from-blue-600 hover:to-blue-800 focus:ring-4 focus:ring-blue-300 active:from-blue-700 disabled:from-gray-50 disabled:via-gray-100 disabled:to-gray-200 disabled:text-gray-400 disabled:shadow-sm disabled:shadow-gray-400/50;
  }

  .stop {
    @apply bg-gradient-to-r from-orange-500 to-orange-700 shadow-orange-500/50 transition-all hover:from-orange-600 hover:to-orange-800 focus:ring-orange-300 active:from-orange-700 disabled:from-gray-50 disabled:via-gray-100 disabled:to-gray-200 disabled:text-gray-400 disabled:shadow-sm disabled:shadow-gray-400/50;
  }

  #preview {
    @apply bg-gradient-to-r from-sky-400 to-sky-600 shadow-sky-500/50 transition-all hover:from-sky-500 hover:to-sky-700 active:from-sky-600 disabled:from-gray-50 disabled:via-gray-100 disabled:to-gray-200 disabled:text-gray-400 disabled:shadow-gray-400/50;
  }
</style>
