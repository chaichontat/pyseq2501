<script lang="ts">
  import Dropdown from "./dropdown.svelte";
  import { userStore as us } from "$src/stores/store";
  import type { Cmd, Ops } from "$src/stores/command";
  import { createEventDispatcher } from "svelte";
  import { checkRange } from "$src/utils";
  import Takeimage from "$src/components/main/takeimage/takeimage.svelte";
  export let n: number;
  export let cmd: Cmd;

  export let fc_: 0 | 1;

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
    <span class="flex gap-x-16 items-center">
      <div><Dropdown bind:cmd /></div>

      <!-- Hold -->
      {#if cmd.op === "hold"}
        <p>
          Time <input type="number" class="w-16 py-1 ml-3 mr-1 pretty font-medium" bind:value={cmd.time} use:checkRange={[0, 99]} min="0" max="99" />
          h
          <input type="number" class="w-16 py-1 ml-3 mr-1 pretty font-medium" bind:value={cmd.time} use:checkRange={[0, 59]} min="0" max="59" />
          m
          <input type="number" class="w-16 py-1 ml-3 mr-1 pretty font-medium" bind:value={cmd.time} use:checkRange={[0, 59]} min="0" max="59" />
          s
        </p>

        <!--  Goto considered harmful -->
      {:else if cmd.op === "goto"}
        <p>
          Go to <input type="number" class="w-16 py-1 mx-2 pretty font-medium" bind:value={cmd.step} use:checkRange={[1, n]} min="1" max={n} />
          for
          <input type="number" class="w-16 py-1 mx-2 pretty font-medium" bind:value={cmd.n} use:checkRange={[1, Infinity]} min="1" />
          times.
        </p>

        <!-- Wash -->
      {:else if cmd.op === "pump"}
        <p>
          <span>
            Reagent
            <select class="pretty mx-2">
              {#each $us.exps[fc_].reagents as { uid, reagent }}
                {#if "port" in reagent}
                  <option>{`${reagent.port} - ${reagent.name}`}</option>
                {:else}
                  <option>{`Group ${reagent.name}`}</option>
                {/if}
              {/each}
            </select>
          </span>

          <span class="ml-4">
            Volume <input type="number" class="w-24 py-1 mx-2 pretty font-medium" use:checkRange={[1, 2000]} min="1" max="2000" bind:value={cmd.volume} />
            μl
          </span>
        </p>

        <!-- Prime -->
      {:else if cmd.op === "prime"}
        <p>
          Reagent
          <select class="text-sm drop">
            {#each $us.exps[fc_].reagents as { uid, reagent }}
              {#if "port" in reagent}
                <option>{`${reagent.port} - ${reagent.name}`}</option>
              {:else}
                <option>{`Group ${reagent.name}`}</option>
              {/if}
            {/each}
          </select>

          <span>
            Volume <input type="number" class="w-24 py-1 mx-2 pretty font-medium" use:checkRange={[1, 2000]} min="1" max="2000" bind:value={cmd.volume} />
            μl
          </span>
        </p>
        <!-- Temp -->
      {:else if cmd.op === "temp"}
        <p>
          Temperature <input type="number" class="w-24 py-1 mx-2 pretty font-medium" use:checkRange={[10, 60]} min="10" max="60" bind:value={cmd.temp} />
          °C
        </p>
      {/if}
      <!-- Image -->
      <!-- {:else if cmd.op === "takeimage"} -->
    </span>

    <!-- <span class="ml-6 text-lg font-medium text-gray-600 ">
      Time: <div class="inline-block font-mono text-xl text-gray-700 whitespace-nowrap">60</div>
      s
    </span> -->

    <!-- Those that require more space. -->
    {#if cmd.op === "takeimage"}
      <div class="grid grid-cols-4 mt-2 font-medium divide-x clump gap-x-4">
        <span class="col-span-4 my-2"><Takeimage bind:params={cmd} inAuto={true} {fc_} /></span>
      </div>
      <!-- content here -->
    {/if}
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

  p {
    @apply font-medium text-lg;
  }

  .minor-box {
    @apply w-24 py-1 mx-2;
  }
</style>
