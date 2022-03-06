<script lang="ts">
  import { onMount } from "svelte";

  import { localStore as ls, userStore as us, cmdStore, statusStore as ss } from "$src/stores/store";
  import { browser } from "$app/env";
  import { Tab, TabGroup, TabList } from "@rgossiaux/svelte-headlessui";
  import Autofocusgraph from "./autofocusgraph.svelte";

  let canvas: HTMLCanvasElement;
  let imgFrame: HTMLImageElement;
  let ctx: CanvasRenderingContext2D | null;

  let step: number = 0;
  const z_max = 60292;
  const z_min = 2621;
  const n_stack = 259;
  const real_steps = [...Array(259)].map((_, i) => Math.round(z_max - ((z_max - z_min) * i) / n_stack));
  let currChannel = 0;

  onMount(() => {
    ctx = canvas.getContext("2d");
  });

  if (browser) {
    imgFrame = new Image();
    imgFrame.onload = () => ctx?.drawImage(imgFrame, 0, 0);
  }
  $: if (browser && $ls.afimg.afimg) {
    console.log($ls.afimg);
    imgFrame.src = $ls.afimg.afimg[n_stack - step - 1];
  }

  function genTabClass(color: string, selected: boolean, enabled: boolean): string {
    let out = `tab-button ${selected ? `text-white` : `${enabled ? `text-gray-700 hover:text-black bg-gray-50 hover:bg-${color}-300` : "text-gray-400"}`}`;
    return out;
  }
</script>

<div class="space-y-12">
  <div class="flex max-w-lg mx-auto gap-x-4">
    <div class="flex-grow">
      <TabGroup on:change={(idx) => (currChannel = idx.detail)}>
        <TabList class="grid grid-cols-4 p-1 space-x-1 rounded-lg bg-gray-50 white-button">
          <Tab let:selected><button class:bg-green-600={selected} class={genTabClass("green", selected, $us.image_params.channels[0])}>Channel 0</button></Tab>
          <Tab let:selected><button class:bg-orange-500={selected} class={genTabClass("orange", selected, $us.image_params.channels[1])}>Channel 1</button></Tab>
          <Tab let:selected><button class:bg-rose-600={selected} class={genTabClass("rose", selected, $us.image_params.channels[2])}>Channel 2</button></Tab>
          <Tab let:selected><button class:bg-amber-800={selected} class={genTabClass("amber", selected, $us.image_params.channels[3])}>Channel 3</button></Tab>
        </TabList>
      </TabGroup>
    </div>

    <button type="button" on:click={() => ($cmdStore = { cmd: "autofocus" })} disabled={$ss.block} class="px-4 py-1 font-medium text-gray-900 rounded-lg w-36 white-button">
      <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 mr-1" viewBox="0 0 20 20" fill="currentColor">
        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clip-rule="evenodd" />
      </svg>
      <span>Autofocus</span>
    </button>
  </div>

  <div class="w-[80%] mx-auto bg-gray-200 h-[1px]" />

  <div class="flex items-center">
    <div class="flex flex-col items-center max-w-md mx-auto gap-y-6">
      <canvas bind:this={canvas} width={256} height={64} />
      <div class="h-[32px]" />

      <!-- Number and Copy -->
      <div class="flex gap-x-4">
        <button
          type="button"
          class="px-4 py-1 text-sm font-medium text-gray-900 rounded-lg white-button disabled:bg-gray-50 disabled:hover:bg-gray-50 disabled:active:bg-gray-50 disabled:text-gray-500"
          on:click={() => (step = 258 - $ls.afimg.laplacian.map((x, i) => [x, i]).reduce((r, a) => (a[0] > r[0] ? a : r))[1])}
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3"
            />
          </svg>
          Jump to Focus
        </button>

        <span class="px-4 py-2 font-medium rounded-lg bg-blue-50 tabular-nums">{real_steps[n_stack - step - 1]}</span>

        <button
          type="button"
          class="px-4 py-1 text-sm font-medium text-gray-900 rounded-lg white-button disabled:bg-gray-50 disabled:hover:bg-gray-50 disabled:active:bg-gray-50 disabled:text-gray-500"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3"
            />
          </svg>
          To Z Obj
        </button>
      </div>

      <input type="range" class="mb-2 range w-[104.5%]" min="0" max="258" bind:value={step} />
      <Autofocusgraph curr={258 - step} />
    </div>
  </div>
</div>

<style lang="postcss">
  .tab-button {
    @apply transition-all duration-100 w-full py-2 text-sm font-medium rounded-lg focus:outline-none focus:ring-2;
  }

  canvas {
    @apply rounded shadow-lg bg-gray-300 scale-[2] -translate-x-[128px];
    background-size: 1rem 1rem;
    background-image: linear-gradient(to right, #fff 1px, transparent 1px), linear-gradient(to bottom, #fff 1px, transparent 1px);
    transform-origin: top left;
  }

  #frame {
    @apply bg-gray-300;
  }
</style>
