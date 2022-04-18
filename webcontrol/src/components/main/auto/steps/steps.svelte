<script lang="ts">
  import { cmdDefaults } from "$src/stores/command";
  import type { NCmd } from "$src/stores/experiment";
  import { userStore as us } from "$src/stores/store";
  import { dndzone } from "svelte-dnd-action";
  import { flip } from "svelte/animate";
  import Cell from "./step_cell.svelte";

  export let fc_: 0 | 1;

  const flipDurationMs = 200;

  // eslint-disable-next-line no-undef
  function handleDndConsider(e: CustomEvent<DndEvent>) {
    $us.exps[fc_].cmds = e.detail.items as NCmd[];
  }

  // eslint-disable-next-line no-undef
  function handleDndFinalize(e: CustomEvent<DndEvent>) {
    $us.exps[fc_].cmds = e.detail.items as NCmd[];
  }
</script>

<div class="my-8 w-full">
  <p class="mt-6 border-b py-3 text-2xl font-bold text-gray-600">Steps</p>

  <section use:dndzone={{ items: $us.exps[fc_].cmds, dropTargetStyle: { outline: "none" }, flipDurationMs }} on:consider={handleDndConsider} on:finalize={handleDndFinalize}>
    {#each $us.exps[fc_].cmds as { uid, cmd }, i (uid)}
      <div animate:flip={{ duration: flipDurationMs }}>
        <Cell {fc_} n={i + 1} bind:cmd on:delete={() => ($us.exps[fc_].cmds = $us.exps[fc_].cmds.filter((v, j) => i != j))} />
      </div>
    {/each}
  </section>

  <!-- Add step -->
  <button
    id="add"
    class="white-clickable inline-flex h-16 w-full items-center justify-center border-y border-gray-300 text-lg font-medium transition-all hover:font-semibold"
    on:click={() => ($us.exps[fc_].cmds = [...$us.exps[fc_].cmds, { uid: $us.max_uid++, cmd: { ...cmdDefaults.takeimage } }])}
  >
    <span class="inline-flex">
      <svg id="inner" stroke-width="1.5" class="my-0.5 -ml-2 mr-1 h-6 w-6 transition-all" fill="none" viewBox="0 0 24 24" stroke="currentColor" xmlns="http://www.w3.org/2000/svg">
        <path stroke-linecap="round" stroke-linejoin="round" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
      </svg>
      Add Step
    </span>
  </button>
</div>

<style lang="postcss">
  #add:hover #inner {
    stroke-width: 2;
  }
</style>
