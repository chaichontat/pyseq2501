<script lang="ts">
  import { browser } from "$app/env";

  import { imgStore, userStore as us, cmdStore, Img } from "$src/store";
  import { onDestroy } from "svelte";

  let curr: null | number;
  let _curr = "  --";
  let height: number = 0;
  let width: number = 0;
  let n_cols: number = 1;
  let n_bundles: number = 1;

  const unsubscribe = cmdStore.subscribe((x: string) => {
    if (browser) {
      fetch(`http://${window.location.hostname}:8000/img`)
        .then((response: Response) => response.json())
        .then((i: Img) => {
          // ctx.clearRect(0, 0, canvas.width, canvas.height);
          $imgStore = i;
        });
    }
  });

  onDestroy(unsubscribe);

  $: height = Math.max($us.image_params.xy1[1], $us.image_params.xy0[1]) - Math.min($us.image_params.xy1[1], $us.image_params.xy0[1]);
  $: width = Math.max($us.image_params.xy1[0], $us.image_params.xy0[0]) - Math.min($us.image_params.xy1[0], $us.image_params.xy0[0]);
  $: n_cols = Math.ceil(width / 0.768);
  $: n_bundles = Math.ceil(height / 0.048);

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

<span class="z-40 flex w-full space-x-2">
  <!-- Buttons -->
  <div class="grid grid-flow-row w-36">
    <button
      type="button"
      class="text-lg transition-colors shadow-md shadow-blue-500/50 text-white bg-blue-600 hover:bg-blue-700 focus:ring-4 active:bg-blue-800 focus:ring-blue-300 font-medium rounded-lg px-4 py-2.5 text-center inline-flex items-center mr-2"
      on:click={() => ($cmdStore = "take")}
    >
      <svg class="w-6 h-6 mr-1 -ml-2" fill="none" viewBox="0 0 24 24" stroke="currentColor" xmlns="http://www.w3.org/2000/svg">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
      </svg>
      Capture
    </button>

    <button
      type="button"
      class="text-lg mt-2 transition-colors shadow-md shadow-blue-500/50 text-white bg-sky-500 hover:bg-sky-600 focus:ring-4 active:bg-sky-700 focus:ring-sky-300 font-medium rounded-lg px-4 py-2.5 text-center inline-flex items-center mr-2"
      on:click={() => ($cmdStore = "take")}
    >
      <svg class="w-6 h-6 mr-1 -ml-2" fill="none" viewBox="0 0 24 24" stroke="currentColor" xmlns="http://www.w3.org/2000/svg">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
      </svg>
      Preview
    </button>
  </div>

  <!-- Big box -->
  <content class="flex-grow px-4 py-2 border rounded-lg border-base-300 ">
    <div class="grid max-w-2xl grid-cols-3">
      <!-- N Bundles -->
      <section class="flex items-center">
        <span class="text-4xl font-bold">
          <span class="font-mono">{_curr}</span>
          /
          <span class="w-32 px-2 font-mono text-4xl font-bold ">{n_bundles * n_cols}</span>
        </span>
      </section>

      <section class="flex flex-col tabular-nums">
        <span>Width {width.toFixed(3)} mm</span>
        <span>Height {height.toFixed(3)} mm</span>
      </section>

      <section class="flex flex-col">
        <span>{n_cols} columns of {n_bundles} bundles</span>
        <span class="opacity-100">Total time: {(n_bundles * n_cols) / 10} s</span>
      </section>
    </div>

    <!-- Lower bar -->
    <div class="">
      Bundles taken
      <progress value={16} class="transition-all progress progress-secondary" />
    </div>
  </content>
</span>

<style lang="postcss">
</style>
