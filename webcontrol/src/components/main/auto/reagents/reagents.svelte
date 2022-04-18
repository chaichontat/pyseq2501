<script lang="ts">
  import { reagentDefault } from "$src/stores/reagent";
  import type { NReagent } from "$src/stores/experiment";
  import { userStore as us } from "$src/stores/store";
  import { dndzone } from "svelte-dnd-action";
  import { flip } from "svelte/animate";
  import { cubicInOut } from "svelte/easing";
  import { fade } from "svelte/transition";
  import Reagentrow from "./reagentrow.svelte";

  export let fc_: 0 | 1;

  const flipDurationMs = 200;
  // eslint-disable-next-line no-undef
  function handleDndConsider(e: CustomEvent<DndEvent>) {
    $us.exps[fc_].reagents = e.detail.items as NReagent[];
  }

  // eslint-disable-next-line no-undef
  function handleDndFinalize(e: CustomEvent<DndEvent>) {
    $us.exps[fc_].reagents = e.detail.items as NReagent[];
  }
</script>

<p class="mt-6 mb-1 text-2xl font-bold text-gray-600">Reagents</p>
<div class="overflow-x-auto sm:-mx-6 lg:-mx-8">
  <div class="inline-block min-w-full py-2 sm:px-6 lg:px-8">
    <div class="overflow-hidden">
      <table class="min-w-full">
        <thead class="border-y border-gray-400 bg-white">
          <tr>
            <th scope="col" class="px-6 py-2 font-medium text-gray-900">Port #</th>
            <th scope="col" class="px-6 py-2 font-medium text-gray-900">Name</th>
            <th scope="col" class="px-6 py-2 text-center font-medium text-gray-900">Prime pull speed (μl/min)</th>
            <th scope="col" class="px-6 py-2 text-center font-medium text-gray-900">Aspiration speed (μl/min)</th>
            <th scope="col" class="px-6 py-2 text-center font-medium text-gray-900">Push speed (μl/min)</th>
            <th scope="col" class="px-6 py-2 text-center font-medium text-gray-900">Hold time (s)</th>
            <th scope="col" class="px-6 py-2 font-medium text-gray-900" />
          </tr>
        </thead>

        <tbody class="border-b" use:dndzone={{ items: $us.exps[fc_].reagents, dropTargetStyle: { outline: "none" }, flipDurationMs }} on:consider={handleDndConsider} on:finalize={handleDndFinalize}>
          {#each $us.exps[fc_].reagents as { uid, reagent }, i (uid)}
            <tr animate:flip={{ duration: flipDurationMs }} in:fade={{ duration: 150, easing: cubicInOut }} class="border-y border-gray-300 bg-white hover:bg-gray-50">
              <Reagentrow
                {fc_}
                bind:reagent
                primed={false}
                on:delete={() => {
                  $us.exps[fc_].reagents = $us.exps[fc_].reagents.filter((v, j) => i != j);
                }}
              />
            </tr>
          {/each}

          <tr class="cursor-pointer">
            <td colspan="8" class="mx-0 h-16 px-0 py-0 font-medium transition-all">
              <div class="flex h-full divide-x">
                <!-- Add group -->
                <button
                  class="white-clickable inline-flex w-1/2 items-center justify-center whitespace-nowrap rounded-bl align-middle font-medium hover:font-semibold"
                  on:click={() => ($us.exps[fc_].reagents = [...$us.exps[fc_].reagents, { uid: $us.max_uid++, reagent: { name: "" } }])}
                >
                  <svg stroke-width="1.75" class="-ml-2 mr-0.5 h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" xmlns="http://www.w3.org/2000/svg">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                  </svg>
                  Add Group
                </button>
                <!-- Add reagent -->
                <button
                  class="align-middlewhitespace-nowrap white-clickable inline-flex w-1/2 items-center justify-center rounded-br font-medium hover:font-semibold"
                  on:click={() => ($us.exps[fc_].reagents = [...$us.exps[fc_].reagents, { uid: $us.max_uid++, reagent: { ...reagentDefault, port: 1 } }])}
                >
                  <svg stroke-width="1.75" class="-ml-2 mr-0.5 h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" xmlns="http://www.w3.org/2000/svg">
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
