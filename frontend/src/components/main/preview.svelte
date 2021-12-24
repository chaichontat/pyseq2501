<script lang="ts">
  import { onMount } from "svelte";
  import Panzoom, { PanzoomObject } from "@panzoom/panzoom";
  import type { Writable } from "svelte/store";
  import { websocketStore } from "../../ws_store";

  let canvas: HTMLCanvasElement;
  let img: HTMLImageElement;
  let pz: PanzoomObject;
  let store: Writable<string>;

  onMount(() => {
    store = websocketStore(`ws://${window.location.hostname}:8000/img`);
    const ctx = canvas.getContext("2d");
    img = new Image();
    img.onload = function () {
      ctx.drawImage(img, 0, 0);
    };
    pz = Panzoom(canvas, { maxZoom: 5 });
    // pz.pan(10, 10);
  });

  $: {
    if (canvas && $store) {
      img.src = "data:image/jpg;base64," + $store;
    }
  }
</script>

<div class="mt-4 center shadow border border-gray-400" on:wheel={pz.zoomWithWheel}>
  <canvas class="" bind:this={canvas} width={1024} height={1024} />
</div>
