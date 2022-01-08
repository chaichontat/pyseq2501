<script lang="ts">
  import { onMount } from "svelte";
  import Panzoom, { PanzoomObject } from "@panzoom/panzoom";
  import { mainStore, userStore } from "../../store";

  let canvas: HTMLCanvasElement;
  let img: HTMLImageElement;
  let pz: PanzoomObject;

  let ctx: CanvasRenderingContext2D;

  onMount(() => {
    ctx = canvas.getContext("2d");
    pz = Panzoom(canvas, { maxZoom: 5 });
    pz.zoom(0.25, { animate: true });

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

  function render() {}

  $: {
    if (canvas && $mainStore) {
      if ($mainStore.n == 1) {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
      }
      img = new Image();
      img.onload = () => ctx.drawImage(img, 0, 128 * ($userStore.n - $mainStore.n));
      img.src = "data:image/jpg;base64," + $mainStore.img;
    }
  }

  // $: if (canvas) ctx.canvas.height = 128 * $userStore.n;
</script>

<div
  class="mt-4 center shadow border border-gray-400"
  on:wheel={pz.zoomWithWheel}
  style="height:75vh;"
>
  <canvas
    id="canvas"
    bind:this={canvas}
    width={2048}
    height={128 * $userStore.n}
    style="border:2px solid #000000;"
  />
</div>

<!-- <svelte:component /> -->
<!-- <Veg /> -->
