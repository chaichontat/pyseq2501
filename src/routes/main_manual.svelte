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

<div class="sticky top-16 z-40 -mx-10 box-border border-b bg-white/[0.95] px-10 pb-6 shadow-md ">
  <div class="h-4 w-full" />
  <ProgressManual bind:stats on:autofocus={() => (tab = "autofocus")} />
</div>

<p class="title mt-6">Capture Parameters</p>
<Takeimage inAuto={false} bind:params={$us.image_params} bind:stats />

<!-- <p class="title">Preview</p> -->
<div class="tabs mt-8 w-full">
  <div class="tab tab-lifted -ml-10 cursor-default" />
  <button class="tab tab-lifted tab-lg font-medium" on:click={() => (tab = "preview")} class:tab-active={tab === "preview"} class:text-gray-800={tab === "preview"}>Preview</button>
  <button class="tab tab-lifted tab-lg font-medium" on:click={() => (tab = "autofocus")} class:tab-active={tab === "autofocus"} class:text-gray-800={tab === "autofocus"}>Autofocus</button>
  <div class="tab tab-lifted flex-1 cursor-default" />
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
