<script lang="ts">
  import { onMount } from "svelte";

  import { localStore as ls, userStore as us, cmdStore, statusStore as ss } from "$src/stores/store";
  import { browser } from "$app/env";
  import { Tab, TabGroup, TabList } from "@rgossiaux/svelte-headlessui";
  import Autofocusgraph from "./autofocusgraph.svelte";

  let canvas: HTMLCanvasElement;
  let imgFrame: HTMLImageElement;
  let ctx: CanvasRenderingContext2D | null;

  let step = 0;
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

  const hoverColors: { [key in string]: string } = {
    green: "hover:bg-green-300 active:bg-green-700",
    orange: "hover:bg-orange-300",
    rose: "hover:bg-rose-300",
    amber: "hover:bg-amber-600",
  };

  function genTabClass(color: string, selected: boolean): string {
    let out = `tab-button transition-all ${selected ? "text-white" : `text-gray-700 hover:text-black bg-gray-50 ${hoverColors[color]}`}`;
    return out;
  }

  function argmax() {
    return 258 - $ls.afimg.laplacian.map((x, i) => [x, i]).reduce((r, a) => (a[0] > r[0] ? a : r))[1];
  }

  $: if ($ls.afimg.laplacian) step = argmax();
</script>

<div class="space-y-12">
  <div class="mx-auto flex max-w-lg gap-x-4">
    <div class="flex-grow">
      <TabGroup on:change={(idx) => (currChannel = idx.detail)}>
        <TabList class="grid grid-cols-4 space-x-1 rounded-lg border border-gray-300 bg-gray-50 p-1 shadow-sm">
          <Tab let:selected><button class:bg-green-600={selected} class={genTabClass("green", selected) + " active:ring-green-500"}>Channel 0</button></Tab>
          <Tab let:selected><button class:bg-orange-500={selected} class={genTabClass("orange", selected) + " active:ring-orange-500"}>Channel 1</button></Tab>
          <Tab let:selected><button class:bg-rose-600={selected} class={genTabClass("rose", selected) + " active:ring-rose-500"}>Channel 2</button></Tab>
          <Tab let:selected><button class:bg-amber-800={selected} class={genTabClass("amber", selected) + " active:ring-amber-500"}>Channel 3</button></Tab>
        </TabList>
      </TabGroup>
    </div>

    <button type="button" on:click={() => ($cmdStore = { cmd: "autofocus" })} disabled={$ss.block} class="white-button w-36 rounded-lg px-4 py-1 font-medium text-gray-900">
      <svg xmlns="http://www.w3.org/2000/svg" class="mr-1 h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clip-rule="evenodd" />
      </svg>
      <span>Autofocus</span>
    </button>
  </div>

  <div class="mx-auto h-[1px] w-[80%] bg-gray-200" />

  <div class="flex items-center">
    <div class="mx-auto flex max-w-md flex-col items-center gap-y-6">
      <canvas bind:this={canvas} width={256} height={64} />
      <div class="h-[32px]" />

      <!-- Number and Copy -->
      <div class="flex w-full content-evenly gap-x-4">
        <button
          type="button"
          class="white-button rounded-lg px-4 py-1 text-sm font-medium text-gray-900 disabled:bg-gray-50 disabled:text-gray-500 disabled:hover:bg-gray-50 disabled:active:bg-gray-50"
          on:click={() => (step = argmax())}
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="mr-1 h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
            <path stroke-linecap="round" stroke-linejoin="round" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
          Jump to Focus
        </button>

        <span class="rounded-lg border border-blue-200 bg-blue-50 px-4 py-2 font-medium tabular-nums shadow-sm">{real_steps[n_stack - step - 1]}</span>

        <button
          type="button"
          class="white-button rounded-lg px-4 py-1 text-sm font-medium text-gray-900 disabled:bg-gray-50 disabled:text-gray-500 disabled:hover:bg-gray-50 disabled:active:bg-gray-50"
          on:click={() => ($us.image_params.z_obj = real_steps[n_stack - step - 1])}
        >
          To Z Obj
          <svg xmlns="http://www.w3.org/2000/svg" class="ml-2 -mr-1 h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
          </svg>
        </button>
      </div>

      <input type="range" class="range mb-2 w-[104.5%]" min="0" max="258" bind:value={step} />
      <Autofocusgraph curr={258 - step} />
    </div>
  </div>
</div>

<style lang="postcss">
  .tab-button {
    @apply w-full rounded-lg py-2 text-sm font-medium transition-all duration-100 focus:outline-none focus:ring-2;
  }

  canvas {
    @apply -translate-x-[128px] scale-[2] rounded bg-gray-300 shadow-lg;
    background-size: 1rem 1rem;
    background-image: linear-gradient(to right, #fff 1px, transparent 1px), linear-gradient(to bottom, #fff 1px, transparent 1px);
    transform-origin: top left;
  }

  #frame {
    @apply bg-gray-300;
  }
</style>
