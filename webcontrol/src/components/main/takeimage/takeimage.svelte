<script lang="ts">
  import { browser } from "$app/env";
  import XYInput from "$comps/main/xy_input.svelte";
  import type { TakeImage } from "$src/stores/command";
  import { cmdStore, statusStore as ss, userStore as us } from "$src/stores/store";
  import tooltip from "$src/tooltip";
  import { checkRange, count } from "$src/utils";
  import Go from "../go.svelte";
  import LaserChannels from "./laserChannels.svelte";
  export let inAuto = true;
  export let params: TakeImage;
  export let stats = { height: 0, width: 0, n_cols: 0, n_bundles: 0, n_z: 1, time: 0 };
  export let z_stack = false;
  export let fc_: 0 | 1 = 0;

  function blockControls(div: HTMLElement | null, changeTo: boolean): void {
    if (div) {
      div.querySelectorAll("input").forEach((el) => (el.disabled = changeTo));
      div.querySelectorAll("select").forEach((el) => (el.disabled = changeTo));
      div.querySelectorAll("button").forEach((el) => (el.disabled = changeTo));
    }
  }

  function updateImageParams() {
    // Necessary to update map.
    $us.image_params.xy0 = params.xy0;
    $us.image_params.xy1 = params.xy1;
  }

  function isInvalid(s: string) {
    if (!s) return true;
    if (!inAuto) return false; // Don't check if not in auto mode.

    const names = $us.exps[fc_].cmds.filter((c) => c.cmd.op === "takeimage").map((c) => (c.cmd as TakeImage).name);
    if (count(names)[s] > 1) return true;
    return false;
  }

  function genTime(t: number): string {
    const d = new Date(t * 1000).toISOString();
    return t > 3600 ? `${d.substring(11, 19)} hrs` : `${d.substring(14, 19)} mins`;
  }

  $: if (browser) blockControls(document.getElementById("control"), $ss.block);

  $: stats.height = Math.max(params.xy1[1], params.xy0[1]) - Math.min(params.xy1[1], params.xy0[1]);
  $: stats.width = Math.max(params.xy1[0], params.xy0[0]) - Math.min(params.xy1[0], params.xy0[0]);
  $: stats.n_cols = stats.width == 0 ? 1 : Math.ceil(stats.width / (0.768 * (1 - params.overlap)));
  $: stats.n_bundles = Math.ceil(stats.height / 0.048);
  $: stats.time = (stats.n_bundles * stats.n_cols) / 20;
  $: stats.n_z = Math.abs(params.z_to - params.z_from) + 1;
</script>

<!-- <div class:hidden={$ss.block} class="absolute z-50  -mx-10 w-full h-96 bg-black/[0.1]" /> -->
<!-- Capture params. -->
<div id="control" class="grid gap-y-6" style="grid-template-columns: minmax(500px, 1fr) 1fr;">
  <section class="flex flex-col text-lg font-medium">
    <p class="mt-1 text-lg">Name</p>
    <div class="flex max-w-[470px] flex-grow gap-x-2">
      <input type="text" class="pretty mb-4 h-12 flex-grow text-lg" bind:value={params.name} class:invalid={isInvalid(params.name)} />
      <!-- {#if inAuto}
        <Go color="sky" cl="text-lg font-semibold shadow-md shadow-sky-700/10 h-12">Preview</Go>
      {/if} -->
    </div>

    {#if !inAuto}
      <p class="text-lg">Image Path</p>
      <input type="text" class="pretty mb-4 max-w-[470px] flex-grow" bind:value={params.path} class:invalid={!params.path} />
    {/if}
  </section>

  <!-- Optics -->
  <section class="font-medium leading-10 ">
    <h2>Laser and Channels</h2>
    <div class="grid min-w-[600px] grid-cols-2" class:opacity-70={$ss.block}>
      <LaserChannels bind:params i={0} />
      <LaserChannels bind:params i={1} />
    </div>
  </section>

  <!-- XY Input -->
  <section class="flex flex-col gap-2" class:-mt-20={inAuto}>
    <h2>Positions</h2>
    <div class="-mt-1 space-y-4">
      <div>
        <p>📌 Corner 1</p>
        <XYInput bind:xy={params.xy0} on:change={updateImageParams} i={0} />
      </div>
      <div>
        <p>📍 Corner 2</p>
        <XYInput bind:xy={params.xy1} on:change={updateImageParams} i={1} />
      </div>
      <div class="flex gap-8">
        <div>
          <p>X-Overlap</p>
          <input type="number" class="pretty w-20 pr-2" bind:value={params.overlap} step="0.01" min="0" max="0.99" use:checkRange={[0.01, 0.99]} />
          (0-1)
        </div>
        <div class="flex flex-col justify-center font-normal">
          <span class="tabular-nums">{stats.width.toFixed(2)} × {stats.height.toFixed(2)} mm.</span>
          <span class="tabular-nums">{stats.n_cols} columns of {stats.n_bundles} bundles.</span>
          <span class="tabular-nums" class:font-semibold={!z_stack}>
            {genTime(stats.time)}
            {#if z_stack}
              per z-stack.
            {/if}
          </span>
        </div>
      </div>
    </div>
  </section>

  <!-- Focus stuffs -->
  <section class="flex flex-col gap-2">
    <h2>Focus</h2>
    <div class="-mt-1 space-y-4">
      <div class="flex space-x-8">
        <div>
          <p>Z Tilt</p>
          <div class="flex gap-2">
            <input type="number" class="pretty w-28" bind:value={params.z_tilt} min="0" max="25000" use:checkRange={[0, 25000]} />
            <Go on:click={() => ($cmdStore = { move: { z_tilt: params.z_tilt } })} disabled={$ss.block} />
          </div>
        </div>
        <div>
          <p>Z Objective</p>
          <span class="flex gap-2">
            <input type="number" class="pretty w-28" bind:value={params.z_obj} min="0" max="60000" use:checkRange={[0, 60000]} />
            <Go on:click={() => ($cmdStore = { move: { z_obj: params.z_obj } })} disabled={$ss.block} />
          </span>
        </div>
      </div>

      <div class="space-y-2">
        <label class="flex items-center gap-x-1">
          <input type="checkbox" class="mr-1 rounded focus:ring-blue-600" bind:checked={z_stack} disabled={$ss.block === "capturing"} />
          <div class="flex divide-x-2">
            <div class="pr-2" class:font-medium={z_stack}>Z-Stack</div>
            {#if z_stack}
              <div class="font-base px-2">
                {stats.n_z} Z step{#if stats.n_z > 1}s{/if} from {params.z_obj + params.z_from * params.z_spacing} to {params.z_obj + params.z_to * params.z_spacing}
              </div>
              <div class="px-2 font-semibold">Total time: {stats.n_z ? genTime(stats.n_z * stats.time) : genTime(stats.time)}.</div>
            {/if}
          </div>
        </label>
        <div class="flex font-medium" id="zBox">
          <span class="color-group flex items-center rounded-l-lg border-l" class:span-disabled={$ss.block || !z_stack} use:tooltip={"Nyquist is 232."}>Spacing</span>
          <input
            type="number"
            min="1"
            max="60000"
            step="1"
            bind:value={params.z_spacing}
            use:checkRange={[1, 60000]}
            class="pretty z-10 h-10 w-28 rounded-none text-center"
            class:disabled={$ss.block || !z_stack}
            disabled={$ss.block || !z_stack}
          />
          <span use:tooltip={"Multiple of Spacing"} class="color-group flex items-center" class:span-disabled={$ss.block || !z_stack}>From</span>
          <input
            type="number"
            min="-100"
            max="100"
            step="1"
            bind:value={params.z_from}
            use:checkRange={[-100, 100]}
            class="pretty z-10 h-10 w-16 rounded-none text-center"
            class:disabled={$ss.block || !z_stack}
            disabled={$ss.block || !z_stack}
          />
          <span use:tooltip={"Multiple of Spacing"} class="color-group flex items-center" class:span-disabled={$ss.block || !z_stack}>To</span>
          <input
            type="number"
            min="-100"
            max="100"
            step="1"
            bind:value={params.z_to}
            use:checkRange={[-100, 100]}
            class="pretty z-10 h-10 w-16 rounded-l-none rounded-r-lg text-center"
            class:disabled={$ss.block || !z_stack}
            disabled={$ss.block || !z_stack}
          />
        </div>
      </div>
    </div>
  </section>
</div>

<style lang="postcss">
  h2 {
    @apply mb-1 text-xl font-semibold text-gray-800;
  }

  p {
    @apply mb-1 font-medium;
  }

  .span-disabled {
    @apply border-gray-200 bg-gray-50 text-gray-500 shadow-none;
  }
</style>
