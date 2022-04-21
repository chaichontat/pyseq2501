<script lang="ts">
  import type { NCmd, NExperiment, NReagent } from "$src/stores/experiment";
  import type { Status } from "$src/stores/status";
  import { cmdStore, localStore as ls, statusStore as ss, userStore as us } from "$src/stores/store";
  import tooltip from "$src/tooltip";
  import { checkRange, flash } from "$src/utils";
  import { onMount } from "svelte";

  let ports = [-1, 2, 3, 4];
  $: ports = $ls.config.ports;

  let selected: number[] = [];
  let v_pull = 250;
  let v_push = 2000;
  let wait = 26;
  let vol = 250;
  let inlet: 2 | 8 = 8;
  let reverse = false;
  let fcs: [boolean, boolean] = [false, false];

  let fcdiv: HTMLSpanElement;
  let inletDiv: HTMLSpanElement;
  let portList: HTMLSelectElement;

  let buttonState: "ok" | "stop" | "disabled" = "ok";
  let currExp: [NExperiment | null, NExperiment | null] = [null, null];

  function genExperiment(sel: number[], fs: [boolean, boolean], i: 0 | 1): NExperiment | null {
    if (!fcs[i]) return null;

    const raw = selected.map((p): NReagent => ({ uid: p, reagent: { name: p.toString(10), port: p, v_pull: v_pull, v_prime: 2000, v_push: v_push, wait: wait } }));
    const cmds: NCmd[] = [{ uid: 0, cmd: { op: "pump", reagent: "group", volume: vol, inlet, reverse } }];
    if (raw.length > 1) cmds.push({ uid: 1, cmd: { op: "goto", step: 1, n: raw.length - 1 } });

    const reagents: NReagent[] = [{ uid: 0, reagent: { name: "group" } }, ...raw];

    const expt: NExperiment = {
      name: `pump${{ 0: "A", 1: "B" }[i]}`,
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
    reverse = false;
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

  onMount(() => {
    if ($ls.config.machine === "HiSeq2000") {
      tooltip(inletDiv, "Inlet selection only available on the HiSeq 2500.");
    }
  });
</script>

<div class="mt-2 ml-6 flex items-center gap-x-6">
  <select multiple class="min-h-[550px] overflow-y-auto rounded-lg px-0 py-0 text-center" bind:value={selected} bind:this={portList}>
    {#each ports as port}
      <option class="px-6 py-1" value={port}>
        {port}
      </option>
    {/each}
  </select>

  <!-- A/B -->
  <section class="flex flex-col gap-y-4">
    <span class="flex flex-col items-center gap-y-1 rounded-lg bg-sky-200/30 pt-1 pb-2 font-medium text-gray-800" bind:this={fcdiv}>
      <legend>Flowcell</legend>
      <span class="flex justify-center space-x-4 ">
        <label>
          <input type="checkbox" bind:checked={fcs[0]} class="mr-0.5 rounded bg-transparent text-indigo-600 focus:ring-indigo-600" />
          A
        </label>
        <label>
          <input type="checkbox" bind:checked={fcs[1]} class="mr-0.5 rounded bg-transparent text-purple-600 focus:ring-purple-600" />
          B
        </label>
      </span>
    </span>

    <button on:click={() => ($ls.config.machine = "HiSeq2500")}>Hi</button>

    <!-- Inlet -->
    <span
      bind:this={inletDiv}
      class={`${$ls.config.machine === "HiSeq2500" ? "bg-sky-200/30" : "bg-gray-200/30 text-gray-300"} -mt-2 flex flex-col items-center gap-y-1 rounded-lg pt-1 pb-2 font-medium text-gray-800`}
    >
      <legend>Inlet</legend>
      <span class="flex -translate-x-1 justify-center space-x-6">
        <label class="ml-2 block text-sm font-medium" on:click={() => (inlet = 2)}>
          <input type="radio" name="inlet" value="2" class="h-4 w-4 border-gray-300 focus:ring-2 focus:ring-blue-300 focus:ring-offset-0" disabled={$ls.config.machine === "HiSeq2000"} />
          2
        </label>

        <label class="ml-2 block text-sm font-medium" on:click={() => (inlet = 8)}>
          <input type="radio" name="inlet" value="8" class="h-4 w-4 border-gray-300 focus:ring-2 focus:ring-blue-300 focus:ring-offset-0" disabled={$ls.config.machine === "HiSeq2000"} checked />
          8
        </label>
      </span>
    </span>

    <div class="flex flex-col gap-y-1">
      <button type="button" on:click={() => (selected = [...ports])} class="white-button justify-center rounded-lg px-4 py-1 text-sm font-medium text-gray-900">
        <span>Select All</span>
      </button>
      <button type="button" on:click={() => (selected = [])} class="white-button justify-center rounded-lg px-4 py-1 text-sm font-medium text-gray-900">
        <span>Select None</span>
      </button>
    </div>

    <div class="flex flex-col gap-y-1 font-medium">
      Pull speed (μL/min)
      <input type="number" min="1" max="60000" step="1" bind:value={v_pull} use:checkRange={[1, 2500]} class="pretty pr-2 text-right" />
    </div>
    <div class="flex flex-col gap-y-1 font-medium">
      Push speed (μL/min)
      <input type="number" min="1" max="60000" step="1" bind:value={v_push} use:checkRange={[1, 2500]} class="pretty pr-2 text-right" />
    </div>
    <div class="flex flex-col gap-y-1 font-medium">
      Wait time (s)
      <input type="number" min="1" max="60000" step="1" bind:value={wait} use:checkRange={[0, 60000]} class="pretty pr-2 text-right" />
    </div>
    <div class="flex flex-col gap-y-1 font-medium">
      Volume (μL)
      <input type="number" min="1" max="60000" step="1" bind:value={vol} use:checkRange={[0, 60000]} class="pretty pr-2 text-right" />
    </div>

    <button
      type="button"
      class="white-button rounded-lg px-4 py-1 text-lg font-semibold transition-all duration-100 disabled:bg-gray-50 disabled:text-gray-500 disabled:hover:bg-gray-50 disabled:active:bg-gray-50"
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

    <button
      type="button"
      class="white-button mx-auto mt-12 w-1/2 rounded-lg px-4 py-1 text-sm font-semibold transition-all duration-100 disabled:bg-gray-50 disabled:text-gray-500 disabled:hover:bg-gray-50 disabled:active:bg-gray-50"
      class:rose={buttonState === "ok"}
      class:orange={buttonState === "stop"}
      tabindex="0"
      on:click={() => {
        reverse = true;
        runExperiment();
      }}
      disabled={buttonState === "disabled"}
    >
      <div class="mx-auto">
        {#if buttonState === "stop"}
          Stop
        {:else}
          Reverse Pump
        {/if}
      </div>
    </button>
  </section>
</div>

<style lang="postcss">
  .run {
    @apply bg-gradient-to-r from-blue-500 to-blue-700 shadow-blue-500/50 transition-all hover:from-blue-600 hover:to-blue-800 focus:ring-4 focus:ring-blue-300 active:from-blue-700 disabled:from-gray-50 disabled:via-gray-100 disabled:to-gray-200 disabled:text-gray-400 disabled:shadow-sm disabled:shadow-gray-400/50;
  }
  .blue {
    @apply border-blue-300 bg-blue-50 text-blue-800 hover:bg-blue-100 active:bg-blue-200;
  }

  .rose {
    @apply border-rose-300 bg-rose-50 text-rose-800 hover:bg-rose-100 active:bg-rose-200;
  }

  .orange {
    @apply border-orange-400 bg-orange-200 text-orange-900 hover:bg-orange-300 active:bg-orange-400;
  }

  input[type="radio"] {
    @apply cursor-pointer;
  }

  input[type="radio"][disabled] {
    @apply cursor-default border-gray-200;
  }

  input[type="radio"][disabled]:checked {
    @apply bg-gray-200;
  }
</style>
