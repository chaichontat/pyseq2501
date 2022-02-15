<script lang="ts">
  import { imgStore, userStore as us, cmdStore, Img } from "$src/store";
  import { onDestroy } from "svelte";

  let curr: null | number;
  let _curr = "  --";
  let height = 0;
  let corrected: boolean = false;

  const unsubscribe = cmdStore.subscribe((x: string) =>
    fetch(`http://${window.location.hostname}:8000/img`)
      .then((response: Response) => response.json())
      .then((i: Img) => {
        // ctx.clearRect(0, 0, canvas.width, canvas.height);
        $imgStore = i;
      })
  );

  onDestroy(unsubscribe);

  $: height = ($us.man_params.n * 128 * 0.375) / 1000;

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

<span class="z-40 flex w-full gap-x-3">
  <!-- Buttons -->
  <content class="grid w-32 grid-row-2 gap-y-2">
    <button
      type="button"
      class="text-lg mt-2 transition-colors shadow-md shadow-blue-500/50 text-white bg-blue-600 hover:bg-blue-700 focus:ring-4 focus:ring-blue-300 font-medium rounded-lg px-4 py-2.5 text-center inline-flex items-center mr-2 dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800"
      on:click={() => ($cmdStore = "take")}
    >
      <svg class="w-6 h-6 mr-1 -ml-2" fill="none" viewBox="0 0 24 24" stroke="currentColor" xmlns="http://www.w3.org/2000/svg">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
      </svg>
      Start
    </button>
  </content>

  <!-- Big box -->
  <content class="flex-grow px-4 py-2 border rounded-lg border-base-300">
    <div class="grid grid-cols-2 ">
      <!-- N Bundles -->
      <div class="flex items-center">
        <span class="text-4xl font-bold">
          <span class="font-mono">{_curr}</span>
          /
          <input type="number" class="w-32 px-2 text-4xl font-bold text-right pretty rounded-xl" min="1" max="999" placeholder="1" bind:value={$us.man_params.n} />
        </span>
        <div class="flex flex-col ml-4 opacity-75">
          <span>Height {height.toFixed(3)} mm</span>
          <span>Total time: {height / 2} s</span>
        </div>
      </div>

      <div class="grid max-w-sm grid-cols-2">
        <p class="font-medium">532nm</p>
        <p class="font-medium">633nm</p>
        <p class="flex flex-col">
          <label class="channel" class:text-gray-500={!$us.man_params.channels[0]}>
            <input type="checkbox" class="mr-1 text-green-500 rounded focus:ring-green-300" bind:checked={$us.man_params.channels[0]} />
            Channel 0
          </label>

          <label class="channel" class:text-gray-500={!$us.man_params.channels[1]}>
            <input type="checkbox" class="mr-1 text-orange-600 rounded focus:ring-orange-300" bind:checked={$us.man_params.channels[1]} />
            Channel 1
          </label>
        </p>
        <p class="flex flex-col">
          <label class="channel" class:text-gray-500={!$us.man_params.channels[2]}>
            <input type="checkbox" class="mr-1 rounded text-rose-700 focus:ring-rose-500" bind:checked={$us.man_params.channels[2]} />
            Channel 2
          </label>
          <label class="channel" class:text-gray-500={!$us.man_params.channels[3]}>
            <input type="checkbox" class="mr-1 rounded text-amber-900 focus:ring-amber-700" bind:checked={$us.man_params.channels[3]} />
            Channel 3
          </label>
        </p>
      </div>
    </div>

    <div class="">
      Bundles taken
      <progress value={16} max={$us.man_params.n} class="transition-all progress progress-secondary" />
    </div>
  </content>
</span>

<style lang="postcss">
</style>
