<script lang="ts">
  import { reagentDefault } from "$src/cmds";
  import type { NReagent } from "$src/store";
  import { userStore as us } from "$src/store";
  import { dndzone } from "svelte-dnd-action";
  import { flip } from "svelte/animate";
  import { cubicInOut } from "svelte/easing";
  import { fade } from "svelte/transition";
  import Reagentrow from "./reagentrow.svelte";

  const flipDurationMs = 200;
  function handleDndConsider(e: CustomEvent<DndEvent>) {
    $us.reagents = e.detail.items as NReagent[];
  }

  function handleDndFinalize(e: CustomEvent<DndEvent>) {
    $us.reagents = e.detail.items as NReagent[];
  }
</script>

<p class="mt-6 mb-1 text-2xl font-bold text-gray-600">Reagents</p>
<div class="overflow-x-auto sm:-mx-6 lg:-mx-8">
  <div class="inline-block min-w-full py-2 sm:px-6 lg:px-8">
    <div class="overflow-hidden">
      <table class="min-w-full">
        <thead class="bg-white border-gray-400 border-y">
          <tr>
            <th scope="col" class="px-6 py-2 font-medium text-gray-900">Port #</th>
            <th scope="col" class="px-6 py-2 font-medium text-gray-900">Name</th>
            <th scope="col" class="px-6 py-2 font-medium text-center text-gray-900">Prime pull speed (μl/min)</th>
            <th scope="col" class="px-6 py-2 font-medium text-center text-gray-900">Aspiration speed (μl/min)</th>
            <th scope="col" class="px-6 py-2 font-medium text-center text-gray-900">Push speed (μl/min)</th>
            <th scope="col" class="px-6 py-2 font-medium text-center text-gray-900">Hold time (s)</th>
            <th scope="col" class="px-6 py-2 font-medium text-gray-900" />
            <th scope="col" class="px-6 py-2 font-medium text-gray-900" />
          </tr>
        </thead>

        <tbody use:dndzone={{ items: $us.reagents, dropTargetStyle: { outline: "none" }, flipDurationMs }} on:consider={handleDndConsider} on:finalize={handleDndFinalize}>
          {#each $us.reagents as { uid, reagent }, i (uid)}
            <tr animate:flip={{ duration: flipDurationMs }} in:fade={{ duration: 150, easing: cubicInOut }} class="bg-white border-b border-gray-300 hover:bg-gray-50">
              <Reagentrow
                bind:reagent
                primed={false}
                on:delete={() => {
                  $us.reagents = $us.reagents.filter((v, j) => i != j);
                }}
              />
            </tr>
          {/each}

          <!-- Add reagent -->

          <tr class="cursor-pointer" on:click={() => ($us.reagents = [...$us.reagents, { uid: $us.max_uid++, reagent: { ...reagentDefault, port: 1 } }])}>
            <td colspan="8" class="h-12 px-0 py-0 mx-0 font-medium border-b transition-all ease-in-out whitespace-nowrap white-clickable hover:font-semibold hover:bg-gray-50 ">
              <span class="inline-flex items-center justify-center w-full align-middle cursor-pointer">
                <svg stroke-width="1.75" class="-ml-2 mr-0.5 w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" xmlns="http://www.w3.org/2000/svg">
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

<!-- <button
  type="button"
  class="mt-2 transition-colors shadow-lg shadow-blue-500/50 text-white bg-blue-600 hover:bg-blue-700 focus:ring-4 focus:ring-blue-300 font-medium rounded-lg px-4 py-2.5 text-center inline-flex items-center mr-2 dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800"
>
  <svg class="w-6 h-6 mr-1 -ml-2" fill="none" viewBox="0 0 24 24" stroke="currentColor" xmlns="http://www.w3.org/2000/svg">
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
  </svg>
  Add Reagent
</button> -->
