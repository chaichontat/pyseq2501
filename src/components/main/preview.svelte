<script lang="ts">
  import { onMount } from "svelte";
  import Panzoom, { PanzoomObject } from "@panzoom/panzoom";
  import { imgStore, userStore } from "../../store";
  import Hist from "./hist.svelte";

  let canvas: HTMLCanvasElement;
  // let hist: HTMLCanvasElement;

  let img: HTMLImageElement;
  // let hist_img: HTMLImageElement;

  let pz: PanzoomObject;

  let ctx: CanvasRenderingContext2D;
  // let ctx_hist: CanvasRenderingContext2D;

  onMount(() => {
    ctx = canvas.getContext("2d");
    // ctx_hist = hist.getContext("2d");
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

<div
  class="mt-4 center shadow border border-gray-400 relative"
  on:wheel={pz.zoomWithWheel}
  style="height:75vh;"
>
  <canvas
    id="canvas"
    bind:this={canvas}
    width={2048}
    height={128 * $userStore.n}
    style="border:2px solid #000000; background-color: gray;"
  />
  <div
    id="histogram"
    class="z-40 absolute bottom-8 right-8 shadow-lg rounded"
    style="width:400px; height:300px; background-color:white;"
  >
    <Hist />
  </div>
  <!-- <canvas
    
    bind:this={hist}
    width={500}
    height={400}
    style="background-color: gray;"
  /> -->
</div>

<!-- <svelte:component /> -->
<!-- <Veg /> -->
