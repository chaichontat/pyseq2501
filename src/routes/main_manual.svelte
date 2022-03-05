<script lang="ts">
  import { browser } from "$app/env";
  import Preview from "$comps/main/preview.svelte";
  import Autofocus from "$src/components/main/autofocus.svelte";
  import ProgressManual from "$src/components/main/manual/progress_manual.svelte";
  import Takeimage from "$src/components/main/takeimage/takeimage.svelte";
  import { statusStore as ss, userStore as us } from "$src/stores/store";

  let stats = { height: 0, width: 0, n_cols: 0, n_bundles: 0, n_z: 1, time: 0 };

  let tab: "preview" | "autofocus" = "preview";

  function blockControls(div: HTMLElement | null, changeTo: boolean): void {
    if (div) {
      div.querySelectorAll("input").forEach((el) => (el.disabled = changeTo));
      div.querySelectorAll("select").forEach((el) => (el.disabled = changeTo));
      div.querySelectorAll("button").forEach((el) => (el.disabled = changeTo));
    }
  }

  $: if (browser) blockControls(document.getElementById("control"), Boolean($ss.block));
</script>

<div class="box-border sticky z-40 -mx-10 px-10 pb-6 shadow-md bg-white/[0.95] border-b top-16 ">
  <div class="w-full h-4" />
  <ProgressManual bind:stats />
</div>

<p class="mt-6 title">Capture Parameters</p>
<Takeimage inAuto={false} bind:params={$us.image_params} bind:stats />

<!-- <p class="title">Preview</p> -->
<div class="w-full mt-8 tabs">
  <div class="-ml-10 cursor-default tab tab-lifted" />
  <button class="font-medium tab tab-lg tab-lifted" on:click={() => (tab = "preview")} class:tab-active={tab === "preview"} class:text-gray-800={tab === "preview"}>Preview</button>
  <button class="font-medium tab tab-lg tab-lifted" on:click={() => (tab = "autofocus")} class:tab-active={tab === "autofocus"} class:text-gray-800={tab === "autofocus"}>Autofocus</button>
  <div class="flex-1 cursor-default tab tab-lifted" />
</div>

<section class:hidden={tab !== "preview"} class="relative">
  <div class="my-4">
    <Preview />
  </div>
</section>

<section class:hidden={tab !== "autofocus"} class="relative">
  <div class="my-6">
    <Autofocus />
  </div>
</section>
