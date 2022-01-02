<script lang="ts">
  import { onMount } from "svelte";
  import Panzoom, { PanzoomObject } from "@panzoom/panzoom";
  import { mainStore } from "../../store";

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
    // pz.pan(10, 10);
  });

  $: {
    if (canvas && $mainStore) {
      img.src = "data:image/jpg;base64," + $mainStore;
    }
  }
</script>

<div class="mt-4 max-h-full center shadow border border-gray-400" on:wheel={pz.zoomWithWheel}>
  <canvas bind:this={canvas} width={1024} height={800} />
</div>
