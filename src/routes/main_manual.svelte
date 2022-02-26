<script lang="ts">
  import { browser } from "$app/env";
  import Preview from "$comps/main/preview.svelte";
  import ProgressManual from "$src/components/main/manual/progress_manual.svelte";
  import Takeimage from "$src/components/main/takeimage/takeimage.svelte";

  import { userStore as us } from "$src/stores/store";

  let stats = { height: 0, width: 0, n_cols: 0, n_bundles: 0, n_z: 1, time: 0 };

  function blockControls(div: HTMLElement | null, changeTo: boolean): void {
    if (div) {
      div.querySelectorAll("input").forEach((el) => (el.disabled = changeTo));
      div.querySelectorAll("select").forEach((el) => (el.disabled = changeTo));
      div.querySelectorAll("button").forEach((el) => (el.disabled = changeTo));
    }
  }

  $: if (browser) blockControls(document.getElementById("control"), $us.block);
</script>

<div class="box-border sticky z-40 -mx-10 px-10 pb-6 shadow-md bg-white/[0.95] border-b top-16 ">
  <div class="w-full h-4" />
  <ProgressManual bind:stats />
</div>

<p class="mt-6 title">Capture Parameters</p>
<Takeimage inAuto={false} bind:params={$us.image_params} bind:stats />

<p class="title">Preview</p>
<Preview />
