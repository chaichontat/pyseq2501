<script lang="ts">
  import Details from "$comps/main/auto/details.svelte";
  import Reagents from "$comps/main/auto/reagents/reagents.svelte";
  import Steps from "$comps/main/auto/steps/steps.svelte";
  import Preview from "$comps/main/preview.svelte";
  import { userStore as us } from "$src/store";
  import { recipeDefault } from "$src/store";
  import ProgressAuto from "./progress_auto.svelte";

  export let fc: 0 | 1;
</script>

<!-- New or Upload -->
<div class="flex items-center">
  <span>
    <button on:click={() => ($us.mode = "automatic")}>
      <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
      </svg>
    </button>
    <p class="inline-block my-4 text-3xl font-extrabold tracking-tight text-gray-700 dark:text-white">Flowcell {fc ? "B" : "A"}</p>
  </span>
  <div class="flex-grow" />
  <button type="button" class="h-10 px-4 py-1 text-base font-medium rounded-lg white-button">
    <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
    </svg>
    Download
  </button>
</div>
<!-- <ProgressAuto fc={fc} /> -->

{#if $us.recipes[fc]}
  <p class="pb-3 mt-8 text-2xl font-bold text-gray-600 border-b">Details</p>
  <Details />
  <Reagents {fc} />
  <Steps {fc} />
  <p class="mt-6 mb-1 text-2xl font-bold text-gray-600">Preview</p>
  <Preview />

  <!-- Editor -->
{:else}
  <div class="flex items-center justify-center w-full h-[50vh]">
    <div class="inline-flex text-2xl rounded-md shadow-sm" role="group">
      <button type="button" class="px-8 py-6 font-medium rounded-l-lg white-button" on:click={() => ($us.recipes[fc] = { ...recipeDefault })}>
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
        </svg>
        New Experiment
      </button>

      <button type="button" class="px-8 py-6 font-medium border-l-0 rounded-r-lg white-button ">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
        </svg>
        Upload
      </button>
    </div>
  </div>
{/if}

<style lang="postcss">
  svg {
    @apply w-8 h-8 mr-1;
  }
</style>
