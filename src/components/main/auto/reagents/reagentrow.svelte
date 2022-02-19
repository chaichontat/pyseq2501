<script lang="ts">
  import type { Reagent, ReagentGroup } from "$src/stores/reagent";
  import { createEventDispatcher } from "svelte";
  import { checkRange } from "$src/utils";

  const dispatch = createEventDispatcher();

  export let primed: boolean = false;
  export let reagent: Reagent | ReagentGroup;

  const count = (names) => names.reduce((a, b) => ({ ...a, [b]: (a[b] || 0) + 1 }), {}); // don't forget to initialize the accumulator
  const duplicates = (dict) => Object.keys(dict).filter((a) => dict[a] > 1);
</script>

{#if !("port" in reagent)}
  <!-- Reagent group -->
  <td colspan="7" class="h-12 px-4 mx-4 text-xl font-medium transition-colors bg-orange-50 hover:bg-orange-100">
    Group <input bind:value={reagent.name} type="text" class="w-32 m-2 text-xl pretty bg-orange-50" required class:invalid={!reagent.name} />
  </td>
{:else}
  <!-- Reagent proper -->
  <td class="px-6 py-2 font-bold text-gray-900 whitespace-nowrap ">
    <input bind:value={reagent.port} type="number" class="w-16 pretty" min="1" max="19" required />
  </td>
  <td class="px-4 text-gray-900 whitespace-nowrap"><input bind:value={reagent.name} class:invalid={!reagent.name} type="text" class="w-full pretty" min="1" max="2000" required /></td>
  <td class="px-4 text-gray-900 whitespace-nowrap">
    <input bind:value={reagent.v_prime} class:invalid={!(1 <= reagent.v_prime && reagent.v_prime <= 2000)} type="number" class="w-full pretty" min="1" max="2000" required />
  </td>
  <td class="px-4 text-gray-900 whitespace-nowrap">
    <input bind:value={reagent.v_pull} type="number" class="w-full pretty" class:invalid={!(1 <= reagent.v_pull && reagent.v_pull <= 2000)} min="1" max="2000" required />
  </td>
  <td class="px-4 text-gray-900 whitespace-nowrap">
    <input bind:value={reagent.v_push} type="number" class="w-full pretty" class:invalid={!(1 <= reagent.v_push && reagent.v_push <= 2000)} min="1" max="2000" required />
  </td>
  <td class="px-4 text-gray-900 whitespace-nowrap">
    <input bind:value={reagent.wait} type="number" class="w-full pretty" class:invalid={!(0 < reagent.wait)} use:checkRange={0} min="0" required />
  </td>
  <td>
    <button
      type="button"
      class="transition-colors shadow focus:ring-4 font-semibold rounded-lg px-4 py-2.5 text-center inline-flex items-center mr-2 text-sm"
      class:blue={!primed}
      class:green={primed}
    >
      <svg xmlns="http://www.w3.org/2000/svg" class="w-3 h-3 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
      </svg>
      Prime
    </button>
  </td>
{/if}
<!-- Close -->
<td on:click={() => dispatch("delete")}>
  <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 ml-2 cursor-pointer" viewBox="0 0 20 20" fill="currentColor">
    <path
      fill-rule="evenodd"
      d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
      clip-rule="evenodd"
      class="s-TGrNU-FH6_7v"
    />
  </svg>
</td>

<style lang="postcss">
  .blue {
    @apply shadow-blue-500/50 text-white bg-blue-600 hover:bg-blue-700 focus:ring-blue-300 dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800;
  }

  .green {
    @apply shadow-green-500/50 text-white bg-green-600 hover:bg-green-700 focus:ring-green-300 dark:bg-green-600 dark:hover:bg-green-700 dark:focus:ring-green-800;
  }
</style>
