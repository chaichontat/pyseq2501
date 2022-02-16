<script lang="ts">
  import Panzoom, { PanzoomObject } from "@panzoom/panzoom";
  import { onDestroy, onMount } from "svelte";
  import { cubicInOut } from "svelte/easing";
  import { fade } from "svelte/transition";
  import { Img, imgStore, userStore as us } from "$src/store";
  import Hist from "./hist.svelte";
  import { Tab, TabGroup, TabList } from "@rgossiaux/svelte-headlessui";
  import { browser } from "$app/env";

  let canvas: HTMLCanvasElement;
  let imgFrame: HTMLImageElement;
  let pz: PanzoomObject;
  let ctx: CanvasRenderingContext2D;
  let showHistogram: boolean = true;
  let currChannel: 0 | 1 | 2 | 3 = 0;

  onMount(() => {
    ctx = canvas.getContext("2d");
    pz = Panzoom(canvas, { maxZoom: 5 });
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

  $: {
    if (browser) imgFrame.src = $imgStore?.img[currChannel];
  }

  // $: if (canvas) ctx.canvas.height = 128 * $userStore.n;

  function genTabClass(color: string, selected: boolean, enabled: boolean): string {
    let out = `tab-button ${selected ? `text-white` : `${enabled ? `text-gray-700 hover:text-black bg-white hover:bg-${color}-300` : "text-gray-400"}`}`;
    return out;
  }
</script>

<!-- Somehow mx-auto is centering -->
<!-- Image -->
<div id="frame" class="relative z-10 w-11/12 mx-auto mt-4 border border-gray-300 rounded-md resize-y min-h-[40vh]">
  <canvas id="canvas" bind:this={canvas} width={1024} height={128} on:wheel={pz.zoomWithWheel} />

  <!-- Tabs -->
  <div class="absolute z-40 w-2/5 h-10 top-4 left-4">
    <TabGroup on:change={(idx) => (currChannel = idx.detail)}>
      <TabList class="grid grid-cols-4 p-1 space-x-1 bg-white shadow rounded-xl opacity-90 ">
        <Tab disabled={!$us.image_params.channels[0]} let:selected><button class:bg-green-600={selected} class={genTabClass("green", selected, $us.image_params.channels[0])}>Channel 0</button></Tab>
        <Tab disabled={!$us.image_params.channels[1]} let:selected><button class:bg-orange-500={selected} class={genTabClass("orange", selected, $us.image_params.channels[1])}>Channel 1</button></Tab>
        <Tab disabled={!$us.image_params.channels[2]} let:selected><button class:bg-rose-600={selected} class={genTabClass("rose", selected, $us.image_params.channels[2])}>Channel 2</button></Tab>
        <Tab disabled={!$us.image_params.channels[3]} let:selected><button class:bg-amber-800={selected} class={genTabClass("amber", selected, $us.image_params.channels[3])}>Channel 3</button></Tab>
      </TabList>
    </TabGroup>
  </div>

  <!-- Show Histogram -->
  <div class="absolute z-40 inline-flex items-center h-12 bg-white border rounded-lg shadow-lg top-4 right-8 opacity-90">
    <span class="mx-4 font-medium cursor-pointer" on:click={() => (showHistogram = !showHistogram)}>
      <input type="checkbox" class="mr-1 text-blue-500 rounded focus:ring-blue-300" bind:checked={showHistogram} />
      Show Histogram
    </span>
  </div>

  <div class:hidden={!showHistogram} id="histogram" class="absolute z-30 p-6 pb-3 bg-white rounded-lg shadow-lg shadow-gray-500 bottom-8 right-8 opacity-90 w-[400px] h-[300px]">
    <Hist hist={$imgStore?.hist[currChannel]} />
  </div>
</div>

<style lang="postcss">
  .tab-button {
    @apply transition-all duration-100 w-full py-2.5 text-sm leading-5 font-medium rounded-lg focus:outline-none focus:ring-2;
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
