<script lang="ts">
  import { statusStore } from "../../store";
  import { flash } from "../../utils";

  let message = "";

  let div: HTMLElement;
  $: {
    if ($statusStore && message !== $statusStore.msg) {
      message = $statusStore.msg;
      flash(div);
    }
  }
</script>

<div class="relative font-mono font-medium py-2 ">
  <div bind:this={div} class="ml-4 absolute w-full h-full rounded-lg" />
  {#if message}
    <div
      class="circle ml-8 transition-all"
      style="--size: 1rem; --color: blue; --duration: 1s"
    />
    <span class="mx-4 text-sm">{message}</span>
  {:else}
    <div class="ml-8" />
    <span class="mx-4 text-sm">Idle</span>
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
