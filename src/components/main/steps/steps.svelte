<script lang="ts" context="module">
  export type NCmd = { n: number; id: number; cmd: Cmds };
</script>

<script lang="ts">
  import type { Cmds } from "$src/cmds";
  import { defaults } from "$src/cmds";
  import { dndzone } from "svelte-dnd-action";
  import { flip } from "svelte/animate";
  import Reagents from "./reagents.svelte";
  import Cell from "./step_cell.svelte";

  export let cmds: NCmd[] = [{ n: 1, id: 0, cmd: { ...defaults.pump } }];

  let uid: number = 1;

  const flipDurationMs = 200;
  function handleDndConsider(e: CustomEvent<DndEvent>) {
    for (const [i, ncmd] of e.detail.items.entries()) {
      ncmd.n = i + 1;
    }
    cmds = e.detail.items as NCmd[];
  }

  function handleDndFinalize(e: CustomEvent<DndEvent>) {
    for (const [i, ncmd] of e.detail.items.entries()) {
      ncmd.n = i + 1;
    } // update the dragged item.
    cmds = e.detail.items as NCmd[];
  }
</script>

<div class="my-8 w-full">
  <p class="text-gray-600 font-bold text-2xl pb-3 border-b">Details</p>
  <div class="grid grid-cols-4 font-medium mt-2 text-lg">
    <div>
      Name <input type="text" class="pretty" />
    </div>
    <div>
      Path <input type="text" class="pretty" />
    </div>
  </div>

  <Reagents />

  <p class="text-gray-600 font-bold text-2xl py-3 border-b mt-6">Steps</p>

  <section use:dndzone={{ items: cmds, flipDurationMs }} on:consider={handleDndConsider} on:finalize={handleDndFinalize}>
    {#each cmds as { n, id, cmd } (id)}
      <div animate:flip={{ duration: flipDurationMs }}><Cell {n} bind:cmd /></div>
    {/each}
  </section>

  <div
    id="add"
    class="text-lg transition-all border-y border-gray-400 hover:border-blue-500 inline-flex items-center justify-center cursor-pointer w-full h-16 font-medium hover:font-semibold white-clickable hover:bg-gray-50"
    on:click={() => {
      cmds.push({ n: cmds.length + 1, id: uid, cmd: { ...defaults.pump } });
      uid += 1;
      cmds = cmds; // necessary for reactivity
    }}
  >
    <span class="inline-flex">
      <svg id="inner" stroke-width="1.5" class="-ml-2 mr-1 w-6 h-6 transition-all my-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" xmlns="http://www.w3.org/2000/svg">
        <path stroke-linecap="round" stroke-linejoin="round" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
      </svg>
      Add Step
    </span>
  </div>
</div>

<style lang="postcss">
  #add:hover #inner {
    stroke-width: 2;
  }
</style>
