<script lang="ts">
  import type { Reagent, ReagentGroup } from "$src/stores/reagent";
  import { createEventDispatcher } from "svelte";
  import { checkRange, count } from "$src/utils";
  import { userStore as us, localStore as ls } from "$src/stores/store";
  const dispatch = createEventDispatcher();

  export let primed = false;
  export let reagent: Reagent | ReagentGroup;
  export let fc_: 0 | 1;
  export let invalid = false;

  let validPorts = [-1, 2, 3, 4];
  $: validPorts = $ls.config.ports;

  function nameInvalid(s: string): boolean {
    if (!s) return true;
    const names = $us.exps[fc_].reagents.map((r) => r.reagent.name);
    if (count(names)[s] > 1) return true;
    return false;
  }

  function portInvalid(p: number): boolean {
    if (!validPorts.includes(p)) return true;
    const ports = $us.exps[fc_].reagents.filter((r) => "port" in r.reagent).map((r) => (r.reagent as Reagent).port);
    if (count(ports)[p] > 1) return true;
    return false;
  }

  // function groupInvalid(s: string) {
  //   const ports = $us.exps[fc_].reagents.filter((r) => "port" in r.reagent).map((r) => (r.reagent as Reagent).port);
  //   if (count(ports)[p] > 1) return true;
  // }
</script>

{#if !("port" in reagent)}
  <!-- Reagent group -->
  <td colspan="7" class="mx-4 h-12 bg-violet-50 px-4 text-xl font-medium transition-colors hover:bg-violet-100">
    Group <input bind:value={reagent.name} class:invalid={nameInvalid(reagent.name)} type="text" class="pretty m-2 w-32 bg-orange-50 text-xl" required />
  </td>
  <!-- Close -->
  <td class="bg-violet-50 hover:bg-violet-100" on:click={() => dispatch("delete")}>
    <svg xmlns="http://www.w3.org/2000/svg" class="ml-2 h-4 w-4 cursor-pointer" viewBox="0 0 20 20" fill="currentColor">
      <path
        fill-rule="evenodd"
        d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
        clip-rule="evenodd"
        class="s-TGrNU-FH6_7v"
      />
    </svg>
  </td>
{:else}
  <!-- Reagent proper -->
  <td class="px-6 py-2 text-gray-900 whitespace-nowrap ">
    <input bind:value={reagent.port} type="number" class:invalid={portInvalid(reagent.port)} class="w-16 font-semibold pretty" min="1" max={Math.max(...validPorts)} required />
  </td>
  <td class="px-4 text-gray-900 whitespace-nowrap">
    <input bind:value={reagent.name} class:invalid={nameInvalid(reagent.name)} type="text" class="w-full font-medium pretty" required />
  </td>
  <td class="px-4 text-gray-900 whitespace-nowrap">
    <input bind:value={reagent.v_prime} type="number" class="w-full pretty" use:checkRange={[1, 2500]} min="1" max="2500" required />
  </td>
  <td class="px-4 text-gray-900 whitespace-nowrap">
    <input bind:value={reagent.v_pull} type="number" class="w-full pretty" use:checkRange={[1, 2500]} min="1" max="2500" required />
  </td>
  <td class="px-4 text-gray-900 whitespace-nowrap">
    <input bind:value={reagent.v_push} type="number" class="w-full pretty" use:checkRange={[1, 2500]} min="1" max="2500" required />
  </td>
  <td class="px-4 text-gray-900 whitespace-nowrap">
    <input bind:value={reagent.wait} type="number" class="w-full pretty" use:checkRange={[0, Infinity]} min="0" required />
  </td>
  <td>
    <button
      type="button"
      class="transition-colors shadow focus:ring-4 font-semibold rounded-lg px-4 py-2.5 text-center inline-flex items-center mr-2 text-sm"
      class:indigo={!primed && fc_ == 0}
      class:purple={!primed && fc_ == 1}
      class:green={primed}
    >
      <svg xmlns="http://www.w3.org/2000/svg" class="w-3 h-3 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
      </svg>
      Prime
    </button>
  </td>

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
{/if}

<style lang="postcss">
  .indigo {
    @apply bg-indigo-600 text-white shadow-indigo-500/50 hover:bg-indigo-700 focus:ring-indigo-300 active:bg-indigo-800;
  }

  .purple {
    @apply bg-purple-600 text-white shadow-purple-500/50 hover:bg-purple-700 focus:ring-purple-300 active:bg-purple-800;
  }

  .green {
    @apply bg-green-600 text-white shadow-green-500/50 hover:bg-green-700 focus:ring-green-300 active:bg-green-800;
  }
</style>
