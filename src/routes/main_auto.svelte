<script lang="ts">
  import Editor from "$src/components/main/auto/editor.svelte";
  import FlowcellCard from "$src/components/main/auto/flowcell_card.svelte";
  import { userStore as us } from "$src/stores/store";
</script>

<!-- <ProgressAuto /> -->
{#if $us.mode === "automatic"}
  <p class="inline-block my-4 text-4xl font-extrabold tracking-tight text-gray-700 dark:text-white">Flowcells</p>
  <div class="flex mt-4 max-w-screen-lg space-x-6">
    <FlowcellCard fc={0} />
    <FlowcellCard fc={1} />
  </div>
{:else if $us.mode === "editingA"}
  <Editor fc={0} />
{:else if $us.mode === "editingB"}
  <Editor fc={1} />
{:else}
  <!-- YOU SHOULD NOT SEE THIS -->
{/if}
