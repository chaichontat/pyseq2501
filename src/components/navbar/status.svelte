<script lang="ts">
  import { statusStore } from "../../stores/store";
  import { flash } from "../../utils";
  import Spinning from "$comps/spinning.svelte";
  import { browser } from "$app/env";
  let message = "Idle";
  const re = /(ing)/;

  let div: HTMLElement;
  $: {
    if (browser && message !== $statusStore.msg) {
      message = $statusStore.msg;
      flash(div);
    }
  }
</script>

<div class="relative py-2 font-mono text-base font-semibold text-gray-800 ">
  <div class="absolute w-full h-full ml-4 rounded-lg" />
  <div class="ml-2">
    {#if message.search(re) == -1}
      <svg aria-label="connected" class="w-5 h-5" role="img" viewBox="0 0 16 16" fill="rgb(26, 127, 55)">
        <path fill-rule="evenodd" d="M13.78 4.22a.75.75 0 010 1.06l-7.25 7.25a.75.75 0 01-1.06 0L2.22 9.28a.75.75 0 011.06-1.06L6 10.94l6.72-6.72a.75.75 0 011.06 0z" />
      </svg>
    {:else}
      <div class="w-5 h-5 translate-x-0.5 translate-y-0.5"><Spinning /></div>
    {/if}
  </div>
  <span class="mx-1 px-2 py-2 rounded-lg" bind:this={div}>{message}</span>
</div>
