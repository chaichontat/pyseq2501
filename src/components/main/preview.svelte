<script lang="ts">
  import { browser } from "$app/env";
  import { localStore as ls } from "$src/stores/store";
  import Panzoom, { PanzoomObject } from "@panzoom/panzoom";
  import { Tab, TabGroup, TabList } from "@rgossiaux/svelte-headlessui";
  import { onMount } from "svelte";
  import Hist from "./hist.svelte";

  let panSpace: HTMLDivElement;
  let canvas: HTMLCanvasElement;
  let imgFrame: HTMLImageElement;
  let pz: PanzoomObject;
  let ctx: CanvasRenderingContext2D | null;
  let showHistogram: boolean = true;
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
<div id="frame" bind:this={panSpace} class="relative z-10 w-11/12 mx-auto mt-4 border border-gray-300 rounded-md resize-y min-h-[60vh]">
  <canvas id="canvas" bind:this={canvas} width={2048} height={128} on:wheel={pz.zoomWithWheel} on:click={() => (currChannel = 1)} />

  <!-- Tabs -->
  <div class="absolute z-40 w-2/5 h-10 top-4 left-4">
    <TabGroup on:change={(idx) => (currChannel = idx.detail)}>
      <TabList class="grid grid-cols-4 p-1 space-x-1 bg-white shadow rounded-xl opacity-90">
        <Tab disabled={!$ls.img.channels[0]} let:selected><button class:bg-green-600={selected} class={genTabClass("green", selected, $ls.img.channels[0])}>Channel 0</button></Tab>
        <Tab disabled={!$ls.img.channels[1]} let:selected><button class:bg-orange-500={selected} class={genTabClass("orange", selected, $ls.img.channels[1])}>Channel 1</button></Tab>
        <Tab disabled={!$ls.img.channels[2]} let:selected><button class:bg-rose-600={selected} class={genTabClass("rose", selected, $ls.img.channels[2])}>Channel 2</button></Tab>
        <Tab disabled={!$ls.img.channels[3]} let:selected><button class:bg-amber-800={selected} class={genTabClass("amber", selected, $ls.img.channels[3])}>Channel 3</button></Tab>
      </TabList>
    </TabGroup>
  </div>

  <button
    class="absolute z-40 inline-flex items-center h-10 px-4 font-medium bg-white border rounded-lg shadow-lg top-4 right-56 opacity-90 white-button"
    on:click={() => {
      // pz.pan(-1024 + (panSpace.clientWidth - 1024), -(panSpace.clientHeight + canvas.height) / 2);
      pz.pan(0, 0); // TODO Deal with with origin = 50 50
    }}
  >
    Center
  </button>

  <!-- Show Histogram -->
  <div class="absolute z-40 inline-flex items-center h-10 bg-white border rounded-lg shadow-lg top-4 right-8 opacity-90">
    <label class="mx-4 font-medium cursor-pointer">
      <input type="checkbox" class="mr-1 text-blue-500 rounded focus:ring-blue-300" bind:checked={showHistogram} on:click={() => (showHistogram = !showHistogram)} />
      Show Histogram
    </label>
  </div>

  <div class:hidden={!showHistogram} id="histogram" class="absolute z-30 p-6 pb-3 bg-white rounded-lg shadow-lg shadow-gray-500 bottom-8 right-8 opacity-90 w-[400px] h-[300px]">
    <Hist hist={$ls.img.hist[currChannel]} />
  </div>
</div>

<style lang="postcss">
  .tab-button {
    @apply transition-all duration-100 w-full py-2 text-sm  rounded-lg focus:outline-none focus:ring-2;
  }

  #canvas {
    @apply shadow-lg  bg-gray-700 rounded-xl ring-4 ring-gray-600 ring-opacity-50;
    background-size: 10rem 10rem;
    background-image: linear-gradient(to right, #ccc 1px, transparent 1px), linear-gradient(to bottom, #ccc 1px, transparent 1px);
  }

  #frame {
    @apply bg-gray-300;
  }
</style>
