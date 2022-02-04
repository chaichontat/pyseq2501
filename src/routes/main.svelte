<script lang="ts">
  import Details from "$comps/main/auto/details.svelte";
  import Reagents from "$comps/main/auto/reagents/reagents.svelte";
  import Steps from "$comps/main/auto/steps/steps.svelte";
  import Preview from "$comps/main/preview.svelte";
  import { userStore as us } from "$src/store";
  import ProgressAuto from "$src/components/main/auto/progress_auto.svelte";
  import ProgressManual from "$src/components/main/manual/progress_manual.svelte";
  import { fade } from "svelte/transition";

  const duration: number = 150;
</script>

<svelte:head>
  <title>PySeq 2501</title>
</svelte:head>

{#if $us.mode === "automatic"}
  <div class="" out:fade={{ duration }} in:fade={{ duration, delay: duration }}>
    <ProgressAuto />

    <p class="pb-3 mt-8 text-2xl font-bold text-gray-600 border-b">Details</p>
    <Details />
    <Reagents />
    <Steps />
    <p class="mt-6 mb-1 text-2xl font-bold text-gray-600">Preview</p>
    <Preview />
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
