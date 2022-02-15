<script lang="ts">
  import Preview from "$comps/main/preview.svelte";
  import { userStore as us } from "$src/store";
  import ProgressManual from "$src/components/main/manual/progress_manual.svelte";
  import Details from "$src/components/main/auto/details.svelte";

  let height = 0;

  $: height = ($us.man_params.n * 128 * 0.375) / 1000;
</script>

<div class="box-border sticky z-40 -mx-10 px-10 pb-6 shadow-md bg-white/[0.95] border-b top-16 ">
  <div class="w-full h-4" />
  <ProgressManual />
</div>

<p class="mt-6 title">Capture Parameters</p>
<!-- Capture params. -->
<div class="grid grid-cols-2 space-x-2">
  <div>
    <Details />
  </div>
</div>

<p class="title">Preview</p>
<Preview />

<style lang="postcss">
  .channel {
    @apply mr-4;
  }
</style>
