<script lang="ts">
  import type { NCmd, NExperiment, NReagent } from "$src/stores/experiment";
  import type { Status } from "$src/stores/status";
  import { cmdStore, statusStore as ss, userStore as us } from "$src/stores/store";
  import { checkRange, flash } from "$src/utils";

  const ports = [...Array(20).keys()].filter((x) => x != 0 && x != 9);
  let selected: number[] = [];
  let v_pull: number = 250;
  let v_push: number = 2000;
  let wait: number = 26;
  let vol: number = 250;
  let fcs: [boolean, boolean] = [false, false];

  let fcdiv: HTMLSpanElement;
  let portList: HTMLSelectElement;

  let buttonState: "ok" | "stop" | "disabled" = "ok";
  let currExp: [NExperiment | null, NExperiment | null] = [null, null];

  function genExperiment(sel: number[], fs: [boolean, boolean], i: 0 | 1): NExperiment | null {
    if (!fcs[i]) return null;

    const raw = selected.map((p): NReagent => ({ uid: p, reagent: { name: p.toString(10), port: p, v_pull: v_pull, v_prime: 2000, v_push: v_push, wait: wait } }));
    const cmds: NCmd[] = [{ uid: 0, cmd: { op: "pump", reagent: "group", volume: vol } }];
    if (raw.length > 1) cmds.push({ uid: 1, cmd: { op: "goto", step: 1, n: raw.length - 1 } });

    const reagents: NReagent[] = [{ uid: 0, reagent: { name: "group" } }, ...raw];

    const expt: NExperiment = {
      name: `pump${i}`,
      path: "",
      fc: Boolean(i),
      reagents,
      cmds,
    };
    return expt;
  }

  function runExperiment() {
    if (fcs.every((f) => !f)) {
      flash(fcdiv);
      return;
    }

    if (selected.length == 0) {
      flash(portList);
      return;
    }
    for (let i = 0; i < 2; i++) {
      if (!fcs[i]) continue;
      currExp[i] = genExperiment(selected, fcs, i as 0 | 1);
      if (currExp[i] == null) return;
      $us.exps[i] = currExp[i] as NExperiment;
      setTimeout(() => ($cmdStore = { fccmd: { fc: Boolean(i), cmd: "start" } }), 400); // For usersettings to sync to server.
      $ss.fcs[i].running = true;
    }
  }

  function isDisabled(s: Status, f: [boolean, boolean]): "ok" | "stop" | "disabled" {
    for (let i = 0; i < 2; i++) {
      if (!f[i]) continue;
      if (s.fcs[i].running) return currExp[i] === $us.exps[i] ? "stop" : "disabled";
    }
    return "ok";
  }

  $: currExp = [genExperiment(selected, fcs, 0), genExperiment(selected, fcs, 1)];
  $: buttonState = isDisabled($ss, fcs);
</script>

<div class="flex items-center mt-2 ml-6 gap-x-6">
  <select multiple class="min-h-[550px] rounded-lg overflow-y-auto text-center px-0 py-0" bind:value={selected} bind:this={portList}>
    {#each ports as port}
      <option class="px-6 py-1" value={port}>
        {port}
      </option>
    {/each}
  </select>

  <div class="flex flex-col gap-y-5">
    <span class="flex flex-col items-center pt-1 pb-2 font-medium text-gray-800 rounded-lg bg-sky-200/30 gap-y-1" bind:this={fcdiv}>
      <p>Flowcell</p>
      <span class="flex justify-center space-x-4 ">
        <label>
          <input type="checkbox" bind:checked={fcs[0]} class="bg-transparent mr-0.5 text-indigo-600 rounded focus:ring-indigo-600" />
          A
        </label>
        <label>
          <input type="checkbox" bind:checked={fcs[1]} class="bg-transparent mr-0.5 text-purple-600 rounded focus:ring-purple-600" />
          B
        </label>
      </span>
    </span>

    <div class="flex flex-col gap-y-1">
      <button type="button" on:click={() => (selected = [...ports])} class="justify-center px-4 py-1 text-sm font-medium text-gray-900 rounded-lg white-button">
        <span>Select All</span>
      </button>
      <button type="button" on:click={() => (selected = [])} class="justify-center px-4 py-1 text-sm font-medium text-gray-900 rounded-lg white-button">
        <span>Select None</span>
      </button>
    </div>

    <div class="flex flex-col font-medium gap-y-1">
      Pull speed (μL/min)
      <input type="number" min="1" max="60000" step="1" bind:value={v_pull} use:checkRange={[1, 2500]} class="pr-2 text-right pretty" />
    </div>
    <div class="flex flex-col font-medium gap-y-1">
      Push speed (μL/min)
      <input type="number" min="1" max="60000" step="1" bind:value={v_push} use:checkRange={[1, 2500]} class="pr-2 text-right pretty" />
    </div>
    <div class="flex flex-col font-medium gap-y-1">
      Wait time (s)
      <input type="number" min="1" max="60000" step="1" bind:value={wait} use:checkRange={[0, 60000]} class="pr-2 text-right pretty" />
    </div>
    <div class="flex flex-col font-medium gap-y-1">
      Volume (μL)
      <input type="number" min="1" max="60000" step="1" bind:value={vol} use:checkRange={[0, 60000]} class="pr-2 text-right pretty" />
    </div>

    <button
      type="button"
      class="px-4 py-1 text-lg font-semibold transition-all duration-100 rounded-lg white-button disabled:bg-gray-50 disabled:hover:bg-gray-50 disabled:active:bg-gray-50 disabled:text-gray-500"
      class:blue={buttonState === "ok"}
      class:orange={buttonState === "stop"}
      tabindex="0"
      on:click={runExperiment}
      disabled={buttonState === "disabled"}
    >
      <div class="mx-auto">
        {#if buttonState === "stop"}
          Stop
        {:else}
          Pump
        {/if}
      </div>
    </button>
  </div>
</div>

<style lang="postcss">
  .run {
    @apply transition-all bg-gradient-to-r from-blue-500 to-blue-700 shadow-blue-500/50 hover:from-blue-600 hover:to-blue-800 focus:ring-4 focus:ring-blue-300 active:from-blue-700 disabled:text-gray-400 disabled:from-gray-50 disabled:via-gray-100 disabled:to-gray-200 disabled:shadow-gray-400/50 disabled:shadow-sm;
  }
  .blue {
    @apply text-blue-800 border-blue-300 hover:bg-blue-100 active:bg-blue-200 bg-blue-50;
  }

  .orange {
    @apply text-orange-800 border-orange-300 hover:bg-orange-100 active:bg-orange-200 bg-orange-50;
  }
</style>
