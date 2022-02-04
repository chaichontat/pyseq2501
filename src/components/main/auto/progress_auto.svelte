<script lang="ts">
  import { imgStore, userStore, cmdStore } from "$src/store";

  let curr: null | number;
  let _curr = "  --";
  let height = 0;
  let corrected: boolean = false;

  function start() {
    if (0 < $userStore.n && $userStore.n < 1000) {
      $imgStore = { cmd: "take", n: $userStore.n };
    } else {
      alert("Invalid number of bundles.");
    }
  }

  $: height = ($userStore.n * 128 * 0.375) / 1000;

  $: {
    if ($imgStore) {
      if (!("cmd" in $imgStore)) {
        curr = $imgStore ? $imgStore.n : -1;
        _curr = curr == -1 ? "--" : curr;
      }
    }
  }

  $: {
    if (corrected) {
      $imgStore = { cmd: "corr", n: $userStore.n };
    } else {
      $imgStore = { cmd: "uncorr", n: $userStore.n };
    }
  }
</script>

<span class="flex flex-row w-full gap-x-3">
  <content class="w-32 grid grid-row-2 gap-y-2">
    <button
      type="button"
      class="text-lg transition-colors shadow-md shadow-blue-500/50 text-white bg-blue-600 hover:bg-blue-700 focus:ring-4 focus:ring-blue-300 font-semibold rounded-lg px-4 py-2.5 text-center dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800"
      on:click={start}
    >
      Start
    </button>
    <button
      type="button"
      class="text-lg transition-colors shadow-md shadow-blue-500/50 text-white bg-indigo-600 hover:bg-indigo-700 focus:ring-4 focus:ring-indigo-300 font-semibold rounded-lg px-4 py-2.5 text-center dark:bg-indigo-600 dark:hover:bg-indigo-700 dark:focus:ring-indigo-800"
      on:click={start}
    >
      Validate
    </button>
  </content>

  <div class="flex-grow border shadow-sm stats border-base-300">
    <div class="stat">
      <div class="stat-figure text-primary">
        <button class="btn loading btn-circle btn-lg bg-base-200 btn-ghost" />
      </div>
      <div class="flex">
        <span class="stat-value">
          <span class="font-mono">{_curr}</span>
          /
          <span class="px-2 text-right stat-value w-36">{$userStore.cmds.length}</span>
        </span>
        <div class="flex flex-col ml-4 opacity-80">
          <span>Height {height.toFixed(3)} mm</span>
          <span>Total time: {height / 2} s</span>
        </div>
      </div>

      <div class="stat-title">Steps done</div>
      <div class="stat-desc">
        <progress value={0} max={$userStore.cmds.length} class="transition-all progress progress-secondary" />
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
