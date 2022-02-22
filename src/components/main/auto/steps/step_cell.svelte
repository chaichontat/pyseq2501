<script lang="ts">
  import Dropdown from "./dropdown.svelte";
  import { userStore as us } from "$src/stores/store";
  import type { Cmds, Ops } from "$src/stores/command";
  import { createEventDispatcher } from "svelte";
  import { checkRange } from "$src/utils";
  import Takeimage from "$src/components/main/takeimage/takeimage.svelte";
  export let fc: 0 | 1;
  export let n: number;
  export let cmd: Cmds;

  // Can dispatch `delete`.
  const dispatch = createEventDispatcher();

  const borderColor: { [key in Ops]: string } = {
    pump: "blue",
    prime: "sky",
    takeimage: "red",
    hold: "green",
    temp: "teal",
    autofocus: "orange",
    goto: "red",
  };

  // $: cmd = { ...cmdDefaults[cmd.op], ...cmd }; // Second overwrites first.
</script>

<li class={`relative flex py-4 pb-6 pl-2 transition-all ease-in-out border-t-2 hover:bg-gray-50 border-${borderColor[cmd.op]}-300`}>
  <!-- Close -->
  <svg xmlns="http://www.w3.org/2000/svg" class="absolute w-5 h-5 -mt-1 cursor-pointer right-2" viewBox="0 0 20 20" fill="currentColor" on:click={() => dispatch("delete")}>
    <path
      fill-rule="evenodd"
      d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
      clip-rule="evenodd"
    />
  </svg>

  <!-- n -->
  <div class="mr-8">
    <span class="flex items-center justify-center text-lg font-bold bg-blue-100 rounded-full w-14 h-14">
      <!-- {#key n} -->
      <div>{n}</div>
      <!-- {/key} -->
    </span>
  </div>

  <div class="w-full mr-8">
    <span class="flex items-center space-x-16">
      <div><Dropdown bind:cmd /></div>
      <span class="text-lg font-medium text-gray-800">
        Total time: <div class="inline-block font-mono text-xl text-gray-700 whitespace-nowrap">60</div>
        s
      </span>
    </span>

    <div class="grid grid-cols-4 mt-2 font-medium divide-x clump gap-x-4">
      <!-- Hold -->
      {#if cmd.op === "hold"}
        <span>
          Time <input type="number" class="w-32 mx-2 pretty" bind:value={cmd.time} use:checkRange={0} min="0" />
          s
        </span>

        <!--  Goto considered harmful -->
      {:else if cmd.op === "goto"}
        <span class="col-span-4">
          Go to <input type="number" class="w-24 mx-2 pretty" bind:value={cmd.step} placeholder="1" />
          for
          <input type="number" class="w-24 mx-2 pretty" bind:value={cmd.n} placeholder="4" />
          times.
        </span>

        <!-- Wash -->
      {:else if cmd.op === "pump"}
        <span>
          Reagent
          <select class="text-sm drop">
            {#each $us.exps[fc].reagents as { uid, reagent }}
              {#if "port" in reagent}
                <option>{`${reagent.port} - ${reagent.name}`}</option>
              {:else}
                <option>{`Group ${reagent.name}`}</option>
              {/if}
            {/each}
          </select>
        </span>
        <span>
          Volume <input type="number" class="w-24 mx-2 pretty" placeholder="2000" bind:value={cmd.volume} />
          μl
        </span>

        <!-- Prime -->
      {:else if cmd.op === "prime"}
        <span>
          Reagent
          <select class="text-sm drop">
            {#each $us.exps[fc].reagents as { uid, reagent }}
              {#if "port" in reagent}
                <option>{`${reagent.port} - ${reagent.name}`}</option>
              {:else}
                <option>{`Group ${reagent.name}`}</option>
              {/if}
            {/each}
          </select>
        </span>
        <span>
          Volume <input type="number" class="w-24 mx-2 pretty" placeholder="2000" bind:value={cmd.volume} />
          μl
        </span>

        <!-- Temp -->
      {:else if cmd.op === "temp"}
        <span class="col-span-4">
          Temperature <input type="number" class="w-24 mx-2 pretty" placeholder="20" bind:value={cmd.temp} />
          °C
        </span>

        <!-- Image -->
      {:else if cmd.op === "takeimage"}
        <span class="col-span-4 my-2"><Takeimage bind:params={cmd} showPath={false} /></span>
      {:else}
        NOT IMPLEMENTED
      {/if}
    </div>
  </div>
</li>

<style lang="postcss">
  .clump span:not(:first-child) {
    @apply pl-4;
  }

  .cb {
    @apply mr-2;
  }

  .channel {
    @apply mb-2 ml-8 font-normal;
  }
</style>
