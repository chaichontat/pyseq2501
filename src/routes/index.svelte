<script lang="ts">
  import Preview from "$comps/main/preview.svelte";
  import { localStore as ls } from "$src/stores/store";
  import ProgressManual from "$src/components/main/manual/progress_manual.svelte";
  import { fade } from "svelte/transition";
  import MainAuto from "./main_auto.svelte";
  import Details from "$src/components/main/auto/details.svelte";
  import MainManual from "./main_manual.svelte";

  const duration = 150;
</script>

{#if $ls.mode !== "manual"}
  <div out:fade={{ duration }} in:fade={{ duration, delay: duration }}>
    <MainAuto />
  </div>
{:else}
  <div out:fade={{ duration }} in:fade={{ duration, delay: duration }}>
    <MainManual />
  </div>
{/if}

<!-- End line -->
<div class="flex h-36">
  <div class="mx-auto w-2/5 self-center border-t border-gray-200" />
</div>
