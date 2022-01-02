<script lang="ts">
  import { mainStore } from "../../store";

  export let full: null | number = 8;
  export let curr: null | number;

  let _curr = "  --";

  $: {
    _curr = curr ? curr.toString() : "--";
  }

  function start() {
    if (0 < full && full < 1000) {
      mainStore.set(JSON.stringify({ cmd: "take", n: full }));
    } else {
      alert("Invalid number of bundles.");
    }
  }
</script>

<span class="flex flex-row gap-x-3 w-full">
  <content class="grid grid-row-2 gap-y-2 w-24">
    <button class="_btn btn--primary" on:click={start}>Start</button>
    <button class="_btn btn--secondary">Cancel</button>
  </content>

  <div class=" border stats border-base-300 flex-grow">
    <div class="stat">
      <div class="stat-figure text-primary">
        <button class="btn loading btn-circle btn-lg bg-base-200 btn-ghost" />
      </div>
      <span class="stat-value">
        <span class="font-mono">{_curr}</span>
        /
        <input
          type="number"
          class="input stat-value w-24"
          min="1"
          max="999"
          placeholder="1"
          bind:value={full}
        />
      </span>
      <div class="stat-title">Bundles taken</div>
      <div class="stat-desc">
        <progress value={curr} max={full} class="progress progress-secondary" />
      </div>
    </div>
  </div>
</span>

<style lang="postcss">
  ._btn {
    @apply text-lg font-medium rounded-lg p-3 border-none;
  }

  .btn--primary {
    @apply bg-blue-500 text-white;
  }

  .btn--secondary {
    @apply bg-gray-100 text-gray-900;
  }
</style>
