<script lang="ts">
  import type { Reagent } from "$src/store";
  import Reagentrow from "./reagentrow.svelte";
  export let rs: Reagent[] = [...Array(20).keys()].map((i) => ({
    port: i,
    name: "",
    v_pull: 100,
    v_prime: 200,
    v_push: 2000,
    wait: 26,
  }));

  export let show: boolean[] = [...Array(20).keys()].map((i) => false);
  show[1] = true;

  function addReagent() {
    for (const [i, s] of show.entries()) {
      if (!s && i > 0 && i != 9) {
        show[i] = true;
        break;
      }
    }
  }
</script>

<p class="text-gray-600 font-bold text-2xl mt-6 mb-1">Reagents</p>
<div class="overflow-x-auto sm:-mx-6 lg:-mx-8">
  <div class="py-2 inline-block min-w-full sm:px-6 lg:px-8">
    <div class="overflow-hidden">
      <table class="min-w-full">
        <thead class="bg-white border-y border-gray-400">
          <tr>
            <th scope="col" class="font-medium text-gray-900 px-6 py-2">Port #</th>
            <th scope="col" class="font-medium text-gray-900 px-6 py-2">Name</th>
            <th scope="col" class="font-medium text-gray-900 px-6 py-2 text-center">Prime pull speed (μl/min)</th>
            <th scope="col" class="font-medium text-gray-900 px-6 py-2 text-center">Aspiration speed (μl/min)</th>
            <th scope="col" class="font-medium text-gray-900 px-6 py-2 text-center">Push speed (μl/min)</th>
            <th scope="col" class="font-medium text-gray-900 px-6 py-2 text-center">Hold time (s)</th>
            <th scope="col" class="font-medium text-gray-900 px-6 py-2" />
            <th scope="col" class="font-medium text-gray-900 px-6 py-2" />
          </tr>
        </thead>

        <tbody>
          {#each show as x, i}
            {#if x}
              <Reagentrow r={rs[i]} primed={true} />
            {/if}
          {/each}
          <tr>
            <td colspan="8" class="transition-all ease-in-out whitespace-nowrap h-12 border-b mx-0 px-0 py-0 font-medium white-clickable hover:font-semibold hover:bg-gray-50 " on:click={addReagent}>
              <span class="inline-flex justify-center w-full cursor-pointer align-middle">
                <svg stroke-width="1.5" class="-ml-2 mr-1 w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" xmlns="http://www.w3.org/2000/svg">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                </svg>
                Add Reagent
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</div>

<button
  type="button"
  class="mt-2 transition-colors shadow-lg shadow-blue-500/50 text-white bg-blue-600 hover:bg-blue-700 focus:ring-4 focus:ring-blue-300 font-medium rounded-lg px-4 py-2.5 text-center inline-flex items-center mr-2 dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800"
>
  <svg class="-ml-2 mr-1 w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" xmlns="http://www.w3.org/2000/svg">
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
  </svg>
  Add Reagent
</button>
