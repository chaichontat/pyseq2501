<script lang="ts">
  export let full: null | number;
  export let curr: null | number;

  let _curr = "--";
  let _full = "--";

  $: {
    _full = full ? full.toString() : "--";
    _curr = curr ? curr.toString() : "--";
  }
</script>

<span class="flex flex-row gap-x-3 w-full">
  <content class="grid grid-row-2 gap-y-2 w-24">
    <button class="_btn btn--primary">Start</button>
    <button class="_btn btn--secondary">Cancel</button>
  </content>

  <div class=" border stats border-base-300 flex-grow">
    <div class="stat">
      <div class="stat-figure text-primary">
        <button class="btn loading btn-circle btn-lg bg-base-200 btn-ghost" />
      </div>
      <div class="stat-value">
        {`${_curr}/`}<input type="number" class="input stat-value w-24" placeholder="1" />
      </div>
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
