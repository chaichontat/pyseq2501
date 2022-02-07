<script lang="ts">
  import { createEventDispatcher } from "svelte";

  export let xy: [number, number] = [0, 0];

  const dispatch = createEventDispatcher();
</script>

<div class="flex gap-4">
  <span>
    X <input type="number" class="w-24 text-right pretty" placeholder="0" bind:value={xy[0]} min="0" max="25" />
    mm
  </span>
  <span>
    Y <input type="number" class="w-24 text-right pretty" placeholder="0" bind:value={xy[1]} min="0" max="75" />
    mm
  </span>
  <button type="button" class="px-4 py-1 text-sm font-medium text-gray-900 rounded-lg white-button">
    <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path
        stroke-linecap="round"
        stroke-linejoin="round"
        stroke-width="2"
        d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3"
      />
    </svg>
    From Current Position
  </button>
  <button type="button" class="px-4 py-1 text-sm font-medium text-gray-900 rounded-lg white-button">
    <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 mr-1" viewBox="0 0 20 20" fill="currentColor">
      <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clip-rule="evenodd" />
    </svg>
    <span>Go & Preview</span>
  </button>
</div>
