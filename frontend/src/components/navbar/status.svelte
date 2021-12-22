<script lang="ts">
  export let message = "d";

  import { afterUpdate } from "svelte";
  import { fade } from "svelte/transition";

  let div: HTMLElement;

  function flash(element) {
    requestAnimationFrame(() => {
      element.style.transition = "none";
      element.style.color = "rgba(255,62,0,1)";
      element.style.backgroundColor = "rgba(255,62,0,0.2)";

      setTimeout(() => {
        element.style.transition = "color 1s, background 1s";
        element.style.color = "";
        element.style.backgroundColor = "";
      });
    });
  }

  afterUpdate(() => {
    flash(div);
  });
</script>

<div bind:this={div} class="font-mono text-sm font-medium">
  {#if message}
    <div class="circle ml-8" style="--size: 1rem; --color: blue; --duration: 1s" />
    <span class="mx-4">{message}</span>
  {/if}
</div>

<style>
  .circle {
    height: var(--size);
    width: var(--size);
    border-color: var(--color) transparent var(--color) var(--color);
    border-width: calc(var(--size) / 8);
    border-style: solid;
    border-image: initial;
    border-radius: 100%;
    animation: var(--duration) linear 0s infinite normal none running rotate;
  }
  @keyframes rotate {
    0% {
      transform: rotate(0);
    }
    100% {
      transform: rotate(360deg);
    }
  }
</style>
