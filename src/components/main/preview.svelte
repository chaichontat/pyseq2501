<script lang="ts">
  import Panzoom, { PanzoomObject } from "@panzoom/panzoom";
  import { onMount } from "svelte";
  import { cubicInOut } from "svelte/easing";
  import { fade } from "svelte/transition";
  import { imgStore, userStore } from "../../store";
  import Hist from "./hist.svelte";

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
        img.onload = () => ctx.drawImage(img, 0, 256 * ($userStore.n - $imgStore.n));
        img.src = $imgStore.img;
      }
    }
  }

  // $: if (canvas) ctx.canvas.height = 128 * $userStore.n;
</script>

<!-- Somehow mx-auto is centering -->
<div class="relative w-11/12 mx-auto mt-4 border border-gray-300 shadow rounded-md" style="height:75vh;">
  <canvas id="canvas" bind:this={canvas} width={2048} height={128 * $userStore.n} on:wheel={pz.zoomWithWheel} style="background-color: gray;" />
  <div class="absolute z-40 inline-flex items-center h-10 bg-white border rounded-lg shadow-md top-4 right-8 opacity-90">
    <span class="mx-4 font-medium cursor-pointer" on:click={() => (showHistogram = !showHistogram)}>
      <input type="checkbox" class="mr-1 text-blue-500 rounded focus:ring-blue-300" bind:checked={showHistogram} />
      Show Histogram
    </span>
  </div>
  {#if showHistogram}
    <div transition:fade={{ duration: 100, easing: cubicInOut }} id="histogram" class="absolute z-40 bg-white rounded shadow-lg bottom-8 right-8 opacity-90" style="width:400px; height:300px">
      <Hist />
    </div>
  {/if}
</div>
