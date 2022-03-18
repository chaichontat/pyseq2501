<script lang="ts">
  import type { NCmd } from "$src/stores/experiment";
  import { cmdStore, localStore, statusStore as ss, userStore as us } from "$src/stores/store";
  import tooltip from "$src/tooltip";
  import type { Tweened } from "svelte/motion";
  import Progress from "../progress.svelte";

  let step: [number, number, number] = [0, 0, 0];
  let progress: Tweened<number>;
  let running = false;
  let n_steps = 1;

  // export let stats: { height: number; width: number; n_cols: number; n_bundles: number; n_z: number; time: number };
  export let fc_: 0 | 1;
  const fc = Boolean(fc_);

  $: running = $ss.fcs[fc_].running;
  $: {
    if ($cmdStore?.step) {
      step = $cmdStore.step;
      // progress.set((step[2] * (stats.n_z * stats.n_bundles) + step[1] * stats.n_bundles + step[0]) / (stats.n_bundles * stats.n_cols * stats.n_z));
    }
  }

  let interval: ReturnType<typeof setInterval> | undefined;
  let t = 0;

  $: startState = running ? "stop" : "ok";
  $: if (!running && interval) clearInterval(interval);

  function handleCapture() {
    if (interval) clearInterval(interval);

    if (running) {
      $cmdStore = { fccmd: { fc, cmd: "stop" } };
    } else {
      t = 0;
      interval = setInterval(() => {
        t += 1;
      }, 1000);
      $cmdStore = { fccmd: { fc, cmd: "start" } };
      $ss.fcs[fc_].running = true;
    }
  }

  function handleValidate() {
    $cmdStore = { fccmd: { fc, cmd: "validate" } };
  }

  function calcSteps(cs: NCmd[]): number {
    let n = cs.length;
    for (const [i, c] of cs.entries()) {
      if (c.cmd.op === "goto") {
        n -= 1; // Get rid of the goto.
        n += c.cmd.n * (i - (c.cmd.step - 1));
      }
    }
    return n;
  }

  $: n_steps = calcSteps($us.exps[fc_].cmds);
</script>

<Progress bind:progress>
  <div slot="buttons" class="grid w-36 grid-flow-row">
    <button
      type="button"
      class="mr-2 mb-2 rounded-lg px-5 py-2.5 text-center text-lg font-medium text-white shadow-lg transition-all focus:ring-4"
      class:start={!running}
      class:stop={running}
      on:click={handleCapture}
      disabled={!$localStore.connected}
    >
      <div class="flex h-12 cursor-pointer items-center text-lg">
        {#if running}
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
          Start
        {/if}
      </div>
    </button>

    <button
      type="button"
      id="preview"
      class="mt-2 mr-2 inline-flex items-center rounded-lg px-4 py-2.5 text-center text-lg font-medium text-white shadow transition-all focus:ring-4 focus:ring-violet-300"
      use:tooltip={"Validate your experiment."}
      on:click={handleValidate}
      disabled={running || !$localStore.connected}
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
        Validate
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
          <span class="w-32 px-2 font-mono text-4xl font-bold">{n_steps}</span>
        </span>
      </div>
      Steps
    </section>
    <section class="flex flex-col">
      <span class="text-lg">Imaging time: {t} s</span>
      <span class="text-lg">Pump time: {t} s</span>
    </section>

    <section class="flex flex-col">
      <span class="text-lg font-medium">Elapsed time: {t} s</span>
      <span class="text-lg font-medium">Total time: {5 / 10} s</span>
    </section>
  </div>
</Progress>

<style lang="postcss">
  .start {
    @apply bg-gradient-to-r from-indigo-500 to-indigo-700 shadow-indigo-500/50 transition-all hover:from-indigo-600 hover:to-indigo-800 focus:ring-4 focus:ring-indigo-300 active:from-indigo-700 disabled:from-gray-50 disabled:via-gray-100 disabled:to-gray-200 disabled:text-gray-400 disabled:shadow-sm disabled:shadow-gray-400/50;
  }

  .stop {
    @apply bg-gradient-to-r from-orange-500 to-orange-700 shadow-orange-500/50 transition-all hover:from-orange-600 hover:to-orange-800 focus:ring-orange-300 active:from-orange-700 disabled:from-gray-50 disabled:via-gray-100 disabled:to-gray-200 disabled:text-gray-400 disabled:shadow-sm disabled:shadow-gray-400/50;
  }

  #preview {
    @apply bg-gradient-to-r from-violet-400 to-violet-600 shadow-violet-500/50 transition-all hover:from-violet-500 hover:to-violet-700 active:from-violet-600 disabled:from-gray-50 disabled:via-gray-100 disabled:to-gray-200 disabled:text-gray-400 disabled:shadow-gray-400/50;
  }
</style>
