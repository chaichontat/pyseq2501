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

<div class="relative font-mono font-medium py-2 ">
  <div bind:this={div} class="ml-4 absolute w-full h-full rounded-lg" />
  {#if message}
    <div class="ml-8">
      <Spinning />
    </div>
    <span class="mx-4">{message}</span>
  {:else}
    <div class="ml-8" />
    <span class="mx-4">Idle</span>
  {/if}
</div>
