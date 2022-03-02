<script lang="ts">
  const ports = [...Array(20).keys()].filter((x) => x != 0 && x != 9);

  let selected: number[] = [];
  import { checkRange } from "$src/utils";
  import Go from "../main/go.svelte";

  let v_pull: number = 2000;
  let v_push: number = 2000;
  let wait: number = 26;
</script>

<div class="flex items-center mt-2 ml-6 gap-x-6 ">
  <select multiple class="min-h-[450px] rounded-lg overflow-y-auto text-center px-0 py-0" bind:value={selected}>
    {#each ports as flavour}
      <option class="px-6 py-2" value={flavour}>
        {flavour}
      </option>
    {/each}
  </select>

  <div class="flex flex-col gap-y-5">
    <span class="flex justify-center space-x-6 font-medium">
      <div>
        <input type="checkbox" class="mr-1 text-indigo-600 rounded focus:ring-indigo-600" />
        A
      </div>
      <div>
        <input type="checkbox" class="mr-1 text-purple-600 rounded focus:ring-purple-600" />
        B
      </div>
    </span>
    <div class="flex flex-col gap-y-1">
      <button type="button" on:click={() => (selected = [...ports])} class="justify-center px-4 py-1 text-sm font-medium text-gray-900 rounded-lg white-button">
        <span>Select All</span>
      </button>
      <button type="button" on:click={() => (selected = [])} class="justify-center px-4 py-1 text-sm font-medium text-gray-900 rounded-lg white-button">
        <span>Select None</span>
      </button>
    </div>

    <div class="flex flex-col font-medium gap-y-1">
      Pull speed (μL/min)
      <input type="number" min="1" max="60000" step="1" bind:value={v_pull} use:checkRange={[1, 2500]} class="pr-2 text-right pretty" />
    </div>
    <div class="flex flex-col font-medium gap-y-1">
      Push speed (μL/min)
      <input type="number" min="1" max="60000" step="1" bind:value={v_push} use:checkRange={[1, 2500]} class="pr-2 text-right pretty" />
    </div>
    <div class="flex flex-col font-medium gap-y-1">
      Wait time (s)
      <input type="number" min="1" max="60000" step="1" bind:value={wait} use:checkRange={[0, 60000]} class="pr-2 text-right pretty" />
    </div>

    <Go cl="text-lg mt-2">Pump</Go>
  </div>
</div>

<style lang="postcss">
  .run {
    @apply transition-all bg-gradient-to-r from-blue-500 to-blue-700 shadow-blue-500/50 hover:from-blue-600 hover:to-blue-800 focus:ring-4 focus:ring-blue-300 active:from-blue-700 disabled:text-gray-400 disabled:from-gray-50 disabled:via-gray-100 disabled:to-gray-200 disabled:shadow-gray-400/50 disabled:shadow-sm;
  }
</style>
