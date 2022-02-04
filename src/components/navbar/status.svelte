<script lang="ts">
  import { statusStore } from "../../store";
  import { flash } from "../../utils";
  import Spinning from "./spinning.svelte";

  let message = "";

  let div: HTMLElement;
  $: {
    if ($statusStore && message !== $statusStore.msg) {
      message = $statusStore.msg;
      flash(div);
    }
  }
</script>

<div class="relative py-2 font-mono font-medium ">
  <div bind:this={div} class="absolute w-full h-full ml-4 rounded-lg" />
  {#if message}
    <div class="ml-8"><Spinning /></div>
    <span class="mx-4">{message}</span>
  {:else}
    <div class="ml-8" />
    <span class="mx-4">Idle</span>
  {/if}
</div>
