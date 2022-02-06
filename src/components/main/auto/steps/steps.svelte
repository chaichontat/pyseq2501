<script lang="ts">
  import { defaults } from "$src/cmds";
  import type { NCmd } from "$src/store";
  import { userStore as us } from "$src/store";
  import { dndzone } from "svelte-dnd-action";
  import { flip } from "svelte/animate";
  import Cell from "./step_cell.svelte";

  const flipDurationMs = 200;
  function handleDndConsider(e: CustomEvent<DndEvent>) {
    $us.cmds = e.detail.items as NCmd[];
  }

  function handleDndFinalize(e: CustomEvent<DndEvent>) {
    $us.cmds = e.detail.items as NCmd[];
  }
</script>

<div class="w-full my-8">
  <p class="py-3 mt-6 text-2xl font-bold text-gray-600 border-b">Steps</p>

  <section use:dndzone={{ items: $us.cmds, dropTargetStyle: { outline: "none" }, flipDurationMs }} on:consider={handleDndConsider} on:finalize={handleDndFinalize}>
    {#each $us.cmds as { uid, cmd }, i (uid)}
      <div animate:flip={{ duration: flipDurationMs }}>
        <Cell n={i + 1} bind:cmd on:delete={() => ($us.cmds = $us.cmds.filter((v, j) => i != j))} />
      </div>
    {/each}
  </section>

  <div
    id="add"
    class="inline-flex items-center justify-center w-full h-16 text-lg font-medium border-gray-400 cursor-pointer transition-all border-y hover:border-blue-500 hover:font-semibold white-clickable hover:bg-gray-50"
    on:click={() => ($us.cmds = [...$us.cmds, { uid: $us.max_uid++, cmd: { ...defaults.image } }])}
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
