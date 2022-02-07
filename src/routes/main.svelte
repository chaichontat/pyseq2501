<script lang="ts">
  import Preview from "$comps/main/preview.svelte";
  import { userStore as us } from "$src/store";
  import ProgressManual from "$src/components/main/manual/progress_manual.svelte";
  import { fade } from "svelte/transition";
  import MainAuto from "./main_auto.svelte";

  const duration: number = 150;
</script>

<svelte:head>
  <title>PySeq 2501</title>
</svelte:head>

{#if $us.mode !== "manual"}
  <div out:fade={{ duration }} in:fade={{ duration, delay: duration }}>
    <MainAuto />
  </div>
{:else}
  <div out:fade={{ duration }} in:fade={{ duration, delay: duration }}>
    <ProgressManual />
    <p class="mt-6 mb-1 text-2xl font-bold text-gray-600">Preview</p>
    <Preview />
  </div>
{/if}

<!-- End line -->
<div class="flex h-36">
  <div class="self-center w-2/5 mx-auto border-t border-gray-400" />
</div>
