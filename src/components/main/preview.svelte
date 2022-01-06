<script lang="ts">
  import { onMount } from "svelte";
  import Panzoom, { PanzoomObject } from "@panzoom/panzoom";
  import { mainStore, userStore } from "../../store";
  import Veg from "./veg.svelte";

  let canvas: HTMLCanvasElement;
  let img: HTMLImageElement;
  let pz: PanzoomObject;

  onMount(() => {
    const ctx = canvas.getContext("2d");
    img = new Image();
    img.onload = function () {
      ctx.drawImage(img, 0, 0);
    };
    pz = Panzoom(canvas, { maxZoom: 5 });

    // var width = 100;
    // var height = 100;
    // var exampledata = new Float32Array(height * width);

    // var xoff = width / 3;
    // var yoff = height / 3;

    // for (let y = 0; y <= height; y++) {
    //   for (let x = 0; x <= width; x++) {
    //     // calculate sine based on distance
    //     const x2 = x - xoff;
    //     const y2 = y - yoff;
    //     const d = Math.sqrt(x2 * x2 + y2 * y2);
    //     const t = Math.sin(d / 6.0);

    //     // save sine
    //     exampledata[y * width + x] = t;
    //   }
    // }

    //   const pl = new plot({
    //     canvas: document.getElementById("canvas"),
    //     data: exampledata,
    //     width: width,
    //     height: height,
    //     domain: [-1, 1],
    //     colorScale: "viridis",
    //   });
    //   pl.render();
    //   // pz.pan(10, 10);
  });

  $: {
    if (canvas && $mainStore) {
      img.src = "data:image/jpg;base64," + $mainStore;
    }
  }
</script>

<div class="mt-4 max-h-full center shadow border border-gray-400" on:wheel={pz.zoomWithWheel}>
  <canvas id="canvas" bind:this={canvas} width={1024} height={800} />
</div>

<!-- <svelte:component /> -->
<!-- <Veg /> -->
