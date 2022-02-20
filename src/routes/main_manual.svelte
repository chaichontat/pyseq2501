<script lang="ts">
  import Preview from "$comps/main/preview.svelte";
  import { userStore as us } from "$src/stores/store";
  import ProgressManual from "$src/components/main/manual/progress_manual.svelte";
  import XYInput from "$comps/main/xy_input.svelte";
  import { browser } from "$app/env";
  import tooltip from "$src/tooltip";
  import Takeimage from "$src/components/main/takeimage/takeimage.svelte";
  let height = 0;

  $: height = (128 * 0.375) / 1000;

  function blockControls(div: HTMLElement | undefined, changeTo: boolean): void {
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
  <ProgressManual />
</div>

<p class="mt-6 title">Capture Parameters</p>
<Takeimage bind:params={$us.image_params} />

<p class="title">Preview</p>
<Preview />
