<script lang="ts">
  import Preview from "$comps/main/preview.svelte";
  import { userStore as us } from "$src/store";
  import ProgressAuto from "$src/components/main/auto/progress_auto.svelte";
  import ProgressManual from "$src/components/main/manual/progress_manual.svelte";
  import { fade } from "svelte/transition";
  import Editor from "$src/components/main/auto/editor.svelte";
  import FlowcellCard from "$src/components/main/auto/flowcell_card.svelte";

  const duration: number = 150;
</script>

<!-- <ProgressAuto /> -->
{#if $us.mode === "automatic"}
  <p class="inline-block my-4 text-3xl font-extrabold tracking-tight text-gray-700 dark:text-white">Flowcells</p>
  <div class="flex max-w-screen-lg space-x-6">
    <FlowcellCard fc={0} />
    <FlowcellCard fc={1} />
  </div>
{:else if $us.mode === "editingA"}
  <Editor fc={0} />
{:else if $us.mode === "editingB"}
  <Editor fc={1} />
{:else}
  YOU SHOULD NOT SEE THIS
{/if}
