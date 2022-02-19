<script lang="ts">
  import Spinning from "$comps/spinning.svelte";
  import { userStore as us, statusStore as status, cmdStore } from "$src/stores/store";
  import { local_to_raw } from "$src/coords";

  export let xy: [number, number] = [-1, -1];

  function move() {
    const raw_coord = local_to_raw($us.image_params.fc, xy[0], xy[1]);
    $us.block = true;
    // $cmdStore = { cmd: "x", n: raw_coord.x };
    // $cmdStore = { cmd: "y", n: raw_coord.y };
  }
</script>

<!-- XY Input -->
<div class="flex gap-x-2">
  <div class="flex font-medium">
    <span class="flex items-center border-l rounded-l-lg color-group" class:span-disabled={$us.block}>X</span>
    <input bind:value={xy[0]} type="number" min="-5" max="30" step="0.01" class="z-10 h-10 text-center rounded-none pretty w-28" disabled={$us.block} />
    <span class="flex items-center color-group" class:span-disabled={$us.block}>Y</span>
    <input bind:value={xy[1]} type="number" min="-5" max="80" step="0.01" class="z-10 h-10 text-center rounded-l-none rounded-r-lg pretty w-28" disabled={$us.block} />
  </div>

  <button
    type="button"
    class="px-4 py-1 text-sm font-medium text-blue-800 border-blue-300 rounded-lg hover:bg-blue-100 active:bg-blue-200 bg-blue-50 white-button disabled:bg-gray-50 disabled:hover:bg-gray-50 disabled:active:bg-gray-50 disabled:text-gray-500"
    tabindex="0"
    on:click={move}
    disabled={Boolean($us.block)}
  >
    {#if !$us.block}
      <div class="ml-4">
        <Spinning color="white" />
      </div>
    {:else}
      Go
    {/if}
  </button>

  <button
    type="button"
    class="px-4 py-1 text-sm font-medium text-gray-900 rounded-lg white-button disabled:bg-gray-50 disabled:hover:bg-gray-50 disabled:active:bg-gray-50 disabled:text-gray-500"
    disabled={$us.block}
  >
    <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path
        stroke-linecap="round"
        stroke-linejoin="round"
        stroke-width="2"
        d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3"
      />
    </svg>
    Current
  </button>
</div>

<style lang="postcss">
  .span-disabled {
    @apply text-gray-500 bg-gray-50 border-gray-200;
  }
</style>
