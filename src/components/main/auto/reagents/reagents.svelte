<script lang="ts">
  import { reagentDefault } from "$src/stores/reagent";
  import type { NReagent } from "$src/stores/experiment";
  import { userStore as us } from "$src/stores/store";
  import { dndzone } from "svelte-dnd-action";
  import { flip } from "svelte/animate";
  import { cubicInOut } from "svelte/easing";
  import { fade } from "svelte/transition";
  import Reagentrow from "./reagentrow.svelte";

  export let fc: 0 | 1;

  const flipDurationMs = 200;
  function handleDndConsider(e: CustomEvent<DndEvent>) {
    $us.exps[fc].reagents = e.detail.items as NReagent[];
  }

  function handleDndFinalize(e: CustomEvent<DndEvent>) {
    $us.exps[fc].reagents = e.detail.items as NReagent[];
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
          </tr>
        </thead>

        <tbody class="border-b" use:dndzone={{ items: $us.exps[fc].reagents, dropTargetStyle: { outline: "none" }, flipDurationMs }} on:consider={handleDndConsider} on:finalize={handleDndFinalize}>
          {#each $us.exps[fc].reagents as { uid, reagent }, i (uid)}
            <tr animate:flip={{ duration: flipDurationMs }} in:fade={{ duration: 150, easing: cubicInOut }} class="bg-white border-gray-300 border-y hover:bg-gray-50">
              <Reagentrow
                bind:reagent
                primed={false}
                on:delete={() => {
                  $us.exps[fc].reagents = $us.exps[fc].reagents.filter((v, j) => i != j);
                }}
              />
            </tr>
          {/each}

          <tr class="cursor-pointer">
            <td colspan="8" class="h-16 px-0 py-0 mx-0 font-medium transition-all">
              <div class="flex h-full divide-x">
                <!-- Add group -->
                <button
                  class="inline-flex items-center justify-center w-1/2 font-medium align-middle rounded-bl whitespace-nowrap white-clickable hover:font-semibold"
                  on:click={() => ($us.exps[fc].reagents = [...$us.exps[fc].reagents, { uid: $us.max_uid++, reagent: { name: "" } }])}
                >
                  <svg stroke-width="1.75" class="-ml-2 mr-0.5 w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" xmlns="http://www.w3.org/2000/svg">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                  </svg>
                  Add Group
                </button>
                <!-- Add reagent -->
                <button
                  class="inline-flex items-center justify-center w-1/2 font-medium rounded-br align-middlewhitespace-nowrap white-clickable hover:font-semibold"
                  on:click={() => ($us.exps[fc].reagents = [...$us.exps[fc].reagents, { uid: $us.max_uid++, reagent: { ...reagentDefault, port: 1 } }])}
                >
                  <svg stroke-width="1.75" class="-ml-2 mr-0.5 w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" xmlns="http://www.w3.org/2000/svg">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                  </svg>
                  Add Reagent
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</div>
