<script lang="ts">
  import Preview from "$comps/main/preview.svelte";
  import { userStore as us } from "$src/store";
  import ProgressManual from "$src/components/main/manual/progress_manual.svelte";
  import { fade } from "svelte/transition";
  import MainAuto from "./main_auto.svelte";
  import Details from "$src/components/main/auto/details.svelte";
  import MainManual from "./main_manual.svelte";

  const duration: number = 150;
</script>

{#if $us.mode !== "manual"}
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
  <div class="self-center w-2/5 mx-auto border-t border-gray-200" />
</div>
