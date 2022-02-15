<script lang="ts">
  import { imgStore, userStore, cmdStore, Img } from "$src/store";

  let curr: null | number;
  let _curr = "  --";
  let height = 0;
  let corrected: boolean = false;

  function start() {
    // if (0 < $userStore.man_params.n && $userStore.man_params.n < 1000) {
    //   $cmdStore = "take";
    // } else {
    //   alert("Invalid number of bundles.");
    // }
    fetch(`http://${window.location.hostname}:8000/img`)
      .then((response: Response) => response.json())
      .then((i: Img) => {
        // ctx.clearRect(0, 0, canvas.width, canvas.height);
        $imgStore = i;
      });
  }

  $: height = ($userStore.man_params.n * 128 * 0.375) / 1000;

  // $: {
  //   if ($imgStore) {
  //     if (!("cmd" in $imgStore)) {
  //       curr = $imgStore ? $imgStore.n : -1;
  //       _curr = curr == -1 ? "--" : curr;
  //     }
  //   }
  // }

  // $: {
  //   if (corrected) {
  //     $cmdStore = "corr";
  //   } else {
  //     $cmdStore = "uncorr";
  //   }
  // }
</script>

<span class="flex flex-row w-full gap-x-3">
  <content class="grid w-32 grid-row-2 gap-y-2">
    <button
      type="button"
      class="text-lg mt-2 transition-colors shadow-md shadow-blue-500/50 text-white bg-blue-600 hover:bg-blue-700 focus:ring-4 focus:ring-blue-300 font-medium rounded-lg px-4 py-2.5 text-center inline-flex items-center mr-2 dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800"
      on:click={start}
    >
      <svg class="w-6 h-6 mr-1 -ml-2" fill="none" viewBox="0 0 24 24" stroke="currentColor" xmlns="http://www.w3.org/2000/svg">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
      </svg>
      Start
    </button>
    <button class="_btn btn--secondary" on:click={() => ($cmdStore = "autofocus")}>Autofocus</button>
  </content>

  <div class="flex-grow border stats border-base-300">
    <div class="stat">
      <div class="stat-figure text-primary">
        <button class="btn loading btn-circle btn-lg bg-base-200 btn-ghost" />
      </div>
      <div class="flex">
        <span class="stat-value">
          <span class="font-mono">{_curr}</span>
          /
          <input type="number" class="px-2 text-right input stat-value w-36" min="1" max="999" placeholder="1" bind:value={$userStore.man_params.n} />
        </span>
        <div class="flex flex-col ml-4 opacity-75">
          <span>Height {height.toFixed(3)} mm</span>
          <span>Total time: {height / 2} s</span>
        </div>
        <div class="flex flex-col ml-4">
          <button class="btn btn-sm btn--secondary" on:click={() => ($cmdStore = "dark")}>Take Dark</button>
          <span>
            Dark Corrected
            <input type="checkbox" bind:checked={corrected} class="mt-2 ml-4 toggle toggle-sm" />
          </span>
        </div>
      </div>

      <div class="stat-title">Bundles taken</div>
      <div class="stat-desc">
        <progress value={16} max={$userStore.man_params.n} class="transition-all progress progress-secondary" />
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
