<script lang="ts">
  import { onMount } from "svelte";
  import websocketStore from "../store";
  import Panzoom, { PanzoomObject } from "@panzoom/panzoom";
  import type { Writable } from "svelte/store";

  let canvas: HTMLCanvasElement;
  let myStore: Writable<string>; // MessageEvent
  let img: HTMLImageElement;
  let pz: PanzoomObject;

  function take() {
    $myStore = "take";
  }

  onMount(() => {
    myStore = websocketStore(`ws://${window.location.hostname}:8000/img`);

    const ctx = canvas.getContext("2d");
    img = new Image();
    img.onload = function () {
      ctx.drawImage(img, 0, 0);
    };
    pz = Panzoom(canvas, { maxZoom: 5 });
    // pz.pan(10, 10);
    // pz.zoom(2, { animate: true });
  });

  $: {
    if (canvas && $myStore) {
      img.src = "data:image/jpg;base64," + $myStore;
    }
  }
</script>

<h1>Welcome to SvelteKit</h1>
<p>Visit <a href="https://kit.svelte.dev">kit.svelte.dev</a> to read the documentation</p>

<button type="button" on:click={take}>Take</button>
<div class="wtf" on:wheel={pz.zoomWithWheel}>
  <canvas bind:this={canvas} width={300} height={300} />
</div>

<style>
  .wtf {
    margin: 30px;
    padding: 80px;
  }
</style>
