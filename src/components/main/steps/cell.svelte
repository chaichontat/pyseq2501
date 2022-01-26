<script lang="ts">
  import Dropdown from "./dropdown.svelte";
  import type { Action } from "$src/store";

  export let curr: Action = "Wash";
  export let n: number = 1;
</script>

<li class="relative flex py-6 border-b border-gray-50">
  <svg xmlns="http://www.w3.org/2000/svg" class="absolute h-5 w-5 -mt-1 right-2" viewBox="0 0 20 20" fill="currentColor">
    <path
      fill-rule="evenodd"
      d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
      clip-rule="evenodd"
    />
  </svg>

  <div class="mr-8">
    <span class="flex justify-center items-center w-14 h-14 bg-blue-50 text-lg font-bold rounded-full">{n}</span>
  </div>

  <div>
    <Dropdown bind:curr />

    <div class="clump grid grid-cols-3 divide-x font-medium">
      {#if curr === "Hold"}
        <span>Time <input type="number" class="mx-2 form w-32" placeholder="60" /> s</span>
      {:else if curr === "Wash"}
        <span>Reagent<input type="number" class="mx-2 form w-24" placeholder="250" /> μl/min</span>
        <span>Volume <input type="number" class="mx-2 form w-24" placeholder="2000" /> μl</span>
      {:else if curr === "Move Stage"}
        <span>X <input type="number" class="mx-2 form w-24" placeholder="2000" /> mm</span>
        <span>Y <input type="number" class="mx-2 form w-24" placeholder="2000" /> mm</span>
      {:else}{/if}
    </div>

    <!-- <h3 class="mb-6 text-lg font-bold font-heading">{}</h3> -->
    <p class="text-lg"><slot /></p>
  </div>
</li>

<style lang="postcss">
  .clump span {
    @apply pr-4;
  }
</style>
