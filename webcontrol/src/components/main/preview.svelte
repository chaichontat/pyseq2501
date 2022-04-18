<script lang="ts">
  import { browser } from "$app/env";
  import { localStore as ls } from "$src/stores/store";
  import type { PanzoomObject } from "@panzoom/panzoom";
  import Panzoom from "@panzoom/panzoom";
  import { Tab, TabGroup, TabList } from "@rgossiaux/svelte-headlessui";
  import { onMount } from "svelte";
  import Hist from "./hist.svelte";

  let panSpace: HTMLDivElement;
  let canvas: HTMLCanvasElement;
  let imgFrame: HTMLImageElement;
  let pz: PanzoomObject;
  let ctx: CanvasRenderingContext2D | null;
  let showHistogram = true;
  let currChannel: 0 | 1 | 2 | 3 = 0;
  let activeChannels: number[] = [0, 1, 2, 3];

  onMount(() => {
    ctx = canvas.getContext("2d");
    pz = Panzoom(canvas, { animate: true, maxZoom: 5, startScale: 0.4, origin: "0 0" });
    // startX: -1024 + (panSpace.clientWidth - 1024), startY: (panSpace.clientHeight + canvas.height) / 2, animate: true
  });

  if (browser) {
    imgFrame = new Image();
    imgFrame.onload = () => ctx?.drawImage(imgFrame, 0, 0);
  }

  // function receivedImage() {
  //   fetch(`http://${window.location.hostname}:8000/img`)
  //     .then((response: Response) => response.json())
  //     .then((i: Img) => {
  //       // ctx.clearRect(0, 0, canvas.width, canvas.height);
  //       currImg = i;
  //     });
  // }

  // const unsubscribe = imgStore.subscribe((value) => receivedImage());
  // onDestroy(unsubscribe);

  // $: if (browser) $: console.log($ls.img.channels);
  // On image update
  $: if (browser && ctx && $ls.img) {
    activeChannels = $ls.img.channels.flatMap((c, i) => (c ? [i] : []));
    ctx.canvas.height = $ls.img.dim[0];
    ctx.canvas.width = $ls.img.dim[1];
    panSpace.style.height = `${Math.min(512, $ls.img.dim[0])}px`;
    console.log($ls.img.channels);

    // Selecting invalid channel.
    if (!$ls.img.channels[currChannel]) {
      const new_idx = $ls.img.channels.findIndex(Boolean) as -1 | 0 | 1 | 2 | 3;
      console.log(new_idx);
      if (new_idx !== -1) currChannel = new_idx;
    }

    imgFrame.src = $ls.img.img[activeChannels.findIndex((c) => c === currChannel)];
  }

  function genTabClass(color: string, selected: boolean, enabled: boolean): string {
    let out = `tab-button ${selected ? `text-white font-semibold` : `${enabled ? `font-semibold text-gray-700 hover:text-black bg-white hover:bg-${color}-300` : "text-gray-400 cursor-default"}`}`;
    return out;
  }
</script>

<!-- Somehow mx-auto is centering -->
<!-- Image -->
<div id="frame" bind:this={panSpace} class="relative z-10 mx-auto mt-4 min-h-[60vh] w-11/12 resize-y rounded-md border border-gray-300">
  <canvas id="canvas" bind:this={canvas} width={2048} height={128} on:wheel={pz.zoomWithWheel} on:click={() => (currChannel = 1)} />

  <!-- Tabs -->
  <div class="absolute top-4 left-4 z-40 h-10 w-2/5">
    <TabGroup on:change={(idx) => (currChannel = idx.detail)}>
      <TabList class="grid grid-cols-4 space-x-1 rounded-xl bg-white p-1 opacity-90 shadow">
        <Tab disabled={!$ls.img.channels[0]} let:selected><button class:bg-green-600={selected} class={genTabClass("green", selected, $ls.img.channels[0])}>Channel 0</button></Tab>
        <Tab disabled={!$ls.img.channels[1]} let:selected><button class:bg-orange-500={selected} class={genTabClass("orange", selected, $ls.img.channels[1])}>Channel 1</button></Tab>
        <Tab disabled={!$ls.img.channels[2]} let:selected><button class:bg-rose-600={selected} class={genTabClass("rose", selected, $ls.img.channels[2])}>Channel 2</button></Tab>
        <Tab disabled={!$ls.img.channels[3]} let:selected><button class:bg-amber-800={selected} class={genTabClass("amber", selected, $ls.img.channels[3])}>Channel 3</button></Tab>
      </TabList>
    </TabGroup>
  </div>

  <button
    class="white-button absolute top-4 right-56 z-40 inline-flex h-10 items-center rounded-lg border bg-white px-4 font-medium opacity-90 shadow-lg"
    on:click={() => {
      // pz.pan(-1024 + (panSpace.clientWidth - 1024), -(panSpace.clientHeight + canvas.height) / 2);
      pz.pan(0, 0); // TODO Deal with with origin = 50 50
    }}
  >
    Center
  </button>

  <!-- Show Histogram -->
  <div class="absolute top-4 right-8 z-40 inline-flex h-10 items-center rounded-lg border bg-white opacity-90 shadow-lg">
    <label class="mx-4 cursor-pointer font-medium">
      <input type="checkbox" class="mr-1 rounded text-blue-500 focus:ring-blue-300" bind:checked={showHistogram} on:click={() => (showHistogram = !showHistogram)} />
      Show Histogram
    </label>
  </div>

  <div class:hidden={!showHistogram} id="histogram" class="absolute bottom-8 right-8 z-30 h-[300px] w-[400px] rounded-lg bg-white p-6 pb-3 opacity-90 shadow-lg shadow-gray-500">
    <Hist hist={$ls.img.hist[currChannel]} />
  </div>
</div>

<style lang="postcss">
  .tab-button {
    @apply w-full rounded-lg py-2 text-sm transition-all  duration-100 focus:outline-none focus:ring-2;
  }

  #canvas {
    @apply rounded-xl  bg-gray-700 shadow-lg ring-4 ring-gray-600 ring-opacity-50;
    background-size: 10rem 10rem;
    background-image: linear-gradient(to right, #ccc 1px, transparent 1px), linear-gradient(to bottom, #ccc 1px, transparent 1px);
  }

  #frame {
    @apply bg-gray-300;
  }
</style>
