<script lang="ts">
  import Details from "$comps/main/auto/details.svelte";
  import Reagents from "$comps/main/auto/reagents/reagents.svelte";
  import Steps from "$comps/main/auto/steps/steps.svelte";
  import Preview from "$comps/main/preview.svelte";
  import ProgressAuto from "$src/components/main/auto/progress_auto.svelte";
  import ProgressManual from "$src/components/main/manual/progress_manual.svelte";
  import { fade } from "svelte/transition";
  import { cubicInOut } from "svelte/easing";
  import { crossfade } from "svelte/transition";
  export let tab: "manual" | "automatic" = "automatic";

  const duration: number = 150;
</script>

<svelte:head>
  <title>PySeq 2501</title>
</svelte:head>
<!-- <script>
  import Graph from "./graph.svelte";
</script> -->

{#if tab === "automatic"}
  <div out:fade={{ duration }} in:fade={{ duration, delay: duration }}>
    <ProgressAuto />

    <p class="text-gray-600 font-bold text-2xl pb-3 border-b">Details</p>
    <Details />
    <Reagents />
    <Steps />
    <p class="text-gray-600 font-bold text-2xl mt-6 mb-1">Preview</p>
    <Preview />
  </div>
{:else}
  <div out:fade={{ duration }} in:fade={{ duration, delay: duration }}>
    <ProgressManual />
    <p class="text-gray-600 font-bold text-2xl mt-6 mb-1">Preview</p>
    <Preview />
  </div>
{/if}

<!-- End line -->
<div class="flex h-36">
  <div class="w-2/5 border-t border-gray-400 self-center mx-auto" />
</div>
