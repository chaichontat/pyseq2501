<script lang="ts">
  import { userStore as us } from "$src/stores/store";
  import XYInput from "$comps/main/xy_input.svelte";
  import { browser } from "$app/env";
  import tooltip from "$src/tooltip";
  import type { TakeImage } from "$src/stores/command";
  import LaserChannels from "./laserChannels.svelte";

  export let showPath: boolean = true;
  export let params: TakeImage;
  let height = 0;

  $: height = (128 * 0.375) / 1000;

  function blockControls(div: HTMLElement | null, changeTo: boolean): void {
    if (div) {
      div.querySelectorAll("input").forEach((el) => (el.disabled = changeTo));
      div.querySelectorAll("select").forEach((el) => (el.disabled = changeTo));
      div.querySelectorAll("button").forEach((el) => (el.disabled = changeTo));
    }
  }

  $: if (browser) blockControls(document.getElementById("control"), $us.block);
</script>

<!-- <div class:hidden={$us.block} class="absolute z-50  -mx-10 w-full h-96 bg-black/[0.1]" /> -->
<!-- Capture params. -->
<div id="control" class="grid grid-cols-2 gap-y-6 gap-x-4">
  <section class="flex flex-col text-lg font-medium">
    <p class="text-lg">Name</p>
    <input type="text" class="max-w-md mt-1 mb-4 pretty" bind:value={params.name} />
    {#if showPath}
      <p class="text-lg">Image Path</p>
      <input type="text" class="max-w-md mt-1 mb-4 pretty" bind:value={params.path} />
    {/if}
  </section>

  <!-- Optics -->
  <section class="font-medium leading-10 ">
    <h2 class="">Laser and Channels</h2>
    <div class="grid grid-cols-2" class:opacity-70={$us.block}>
      <LaserChannels bind:params i={0} />
      <LaserChannels bind:params i={1} />
    </div>
  </section>

  <!-- XY Input -->
  <section class="flex flex-col gap-2">
    <h2>Positions</h2>
    <div class="-mt-1 space-y-2">
      <div>
        <p class="mb-1">📌 Corner 1</p>
        <XYInput bind:xy={params.xy0} />
      </div>
      <div>
        <p class="mb-1">📍 Corner 2</p>
        <XYInput bind:xy={params.xy1} />
      </div>
      <div>
        <p class="mb-1">X-Overlap</p>
        <input type="number" class="w-20 pretty pr-2" bind:value={params.overlap} step="0.01" min="0" max="0.99" />
        (0-1)
      </div>
    </div>
  </section>

  <!-- Focus stuffs -->
  <section class="flex flex-col gap-2">
    <h2>Focus</h2>
    <div class="-mt-1 space-y-2">
      <div>
        <p>Z Tilt</p>
        <input type="number" class="w-28 pretty" bind:value={params.z_tilt} />
      </div>

      <div>
        Z Objective
        <span class="flex gap-2">
          <input type="number" class="w-28 pretty" bind:value={params.z_obj} />
          <button type="button" class="px-4 py-1 font-medium text-gray-900 rounded-lg h-11 w-36 white-button">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 mr-1" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clip-rule="evenodd" />
            </svg>
            <span>Autofocus</span>
          </button>
        </span>
      </div>

      <div>
        Z-Stack
        <div class="flex font-medium">
          <span class="flex items-center border-l rounded-l-lg color-group" class:span-disabled={$us.block}>Spacing</span>
          <input type="number" min="1" max="60000" step="0.01" class="z-10 h-10 text-center rounded-none pretty w-28" disabled={$us.block} />
          <span use:tooltip={"Multiple of Spacing"} class="flex items-center color-group" class:span-disabled={$us.block}>From</span>
          <input type="number" min="-100" max="100" step="0.01" class="z-10 h-10 text-center rounded-none pretty w-28 " disabled={$us.block} />
          <span use:tooltip={"Multiple of Spacing"} class="flex items-center color-group" class:span-disabled={$us.block}>To</span>
          <input type="number" min="-100" max="100" step="0.01" class="z-10 w-20 h-10 text-center rounded-l-none rounded-r-lg pretty" disabled={$us.block} />
        </div>
      </div>
    </div>
  </section>
</div>

<style lang="postcss">
  h2 {
    @apply mb-1 text-xl font-semibold text-gray-800;
  }

  .zstack-disabled {
    @apply text-gray-500 bg-gray-50 border-gray-200;
  }
</style>
