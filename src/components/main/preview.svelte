<script lang="ts">
  import Panzoom, { PanzoomObject } from "@panzoom/panzoom";
  import { onMount } from "svelte";
  import { cubicInOut } from "svelte/easing";
  import { fade } from "svelte/transition";
  import { imgStore, userStore as us } from "$src/store";
  import Hist from "./hist.svelte";
  import { Tab, TabGroup, TabList } from "@rgossiaux/svelte-headlessui";

  let canvas: HTMLCanvasElement;
  let img: HTMLImageElement;
  let pz: PanzoomObject;
  let ctx: CanvasRenderingContext2D;
  let showHistogram: boolean = true;

  onMount(() => {
    ctx = canvas.getContext("2d");
    pz = Panzoom(canvas, { maxZoom: 5 });
  });

  $: {
    if (canvas && $imgStore) {
      if (!("cmd" in $imgStore)) {
        console.log($imgStore);
        if ($imgStore.n == 1) {
          ctx.clearRect(0, 0, canvas.width, canvas.height);
        }
        console.log($imgStore);

        img = new Image();
        img.onload = () => ctx.drawImage(img, 0, 256 * ($us.n - $imgStore.n));
        img.src = $imgStore.img;
      }
    }
  }

  // $: if (canvas) ctx.canvas.height = 128 * $userStore.n;

  function genTabClass(color: string, level: number, selected: boolean, enabled: boolean): string {
    let out = `tab-button ${selected ? `bg-white-shadow text-white bg-${color}-${level}` : `${enabled ? `text-gray-700 hover:text-black hover:bg-${color}-300` : "text-gray-400"}`}`;
    console.log(out);
    return out;
  }
</script>

<!-- Somehow mx-auto is centering -->
<div class="relative w-11/12 mx-auto mt-4 border border-gray-300 rounded-md" style="height:75vh;">
  <canvas id="canvas" bind:this={canvas} width={2048} height={128 * $us.n} on:wheel={pz.zoomWithWheel} style="background-color: gray;" />

  <!-- Tabs -->
  <div class="absolute z-40 w-2/5 h-10 top-4 left-4">
    <TabGroup>
      <TabList class="grid grid-cols-4 p-1 space-x-1 bg-white shadow rounded-xl opacity-90 ">
        <Tab disabled={!$us.man_params.channels[0]} let:selected><button class={genTabClass("green", 600, selected, $us.man_params.channels[0])}>Channel 0</button></Tab>
        <Tab disabled={!$us.man_params.channels[1]} let:selected><button class={genTabClass("orange", 500, selected, $us.man_params.channels[1])}>Channel 1</button></Tab>
        <Tab disabled={!$us.man_params.channels[2]} let:selected><button class={genTabClass("rose", 600, selected, $us.man_params.channels[2])}>Channel 2</button></Tab>
        <Tab disabled={!$us.man_params.channels[3]} let:selected><button class={genTabClass("amber", 800, selected, $us.man_params.channels[3])}>Channel 3</button></Tab>
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

  {#if showHistogram}
    <div transition:fade={{ duration: 100, easing: cubicInOut }} id="histogram" class="absolute z-40 bg-white rounded-lg shadow-lg bottom-8 right-8 opacity-90" style="width:400px; height:300px">
      <Hist />
    </div>
  {/if}
</div>

<style lang="postcss">
  .tab-button {
    @apply transition-all duration-100 w-full py-2.5 text-sm leading-5 font-medium rounded-lg focus:outline-none focus:ring-2;
  }
</style>
