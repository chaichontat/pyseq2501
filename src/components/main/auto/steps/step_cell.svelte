<script lang="ts">
  import Dropdown from "./dropdown.svelte";
  import { userStore as us } from "$src/stores/store";
  import type { Cmds } from "$src/stores/command";
  import { cmdDefaults } from "$src/stores/command";
  import Setxy from "./setxy.svelte";
  import { createEventDispatcher } from "svelte";
  import { checkRange } from "$src/utils";
  export let fc: 0 | 1;
  export let n: number;
  export let cmd: Cmds;

  // Can dispatch `delete`.
  const dispatch = createEventDispatcher();

  // $: cmd = { ...cmdDefaults[cmd.op], ...cmd }; // Second overwrites first.
</script>

<li class="relative flex py-4 pl-2 border-t border-gray-300 transition-all ease-in-out hover:bg-gray-50">
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
      <span class="text-lg font-medium text-gray-700">
        Total time: <div class="inline-block font-mono whitespace-nowrap">60</div>
        s
      </span>
    </span>

    <div class="mt-2 font-medium grid grid-cols-4 divide-x clump gap-x-4">
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
        <span>
          Temperature <input type="number" class="w-24 mx-2 pretty" placeholder="20" bind:value={cmd.temp} />
          °C
        </span>

        <!-- Image -->
      {:else if cmd.op === "takeimage"}
        <span>
          Z <input type="number" class="w-24 mx-2 pretty" placeholder="2000" bind:value={cmd.z_tilt} />
          <button type="button" class="px-4 py-1 text-sm font-medium text-gray-900 rounded-lg white-button">
            <span>Move Z</span>
          </button>
        </span>

        <div class="pl-4 mt-4 ml-2 col-span-4">
          <p class="mb-2 text-lg">Upper left</p>
          <Setxy bind:xy={cmd.xy1} />
        </div>

        <div class="pl-4 mt-4 ml-2 col-span-4">
          <p class="mb-2 text-lg gap-x-8">Lower right</p>
          <Setxy bind:xy={cmd.xy0} />
        </div>

        <!-- Channels -->
        <div class="pl-4 mt-4 ml-2 col-span-4">
          <p class="mb-2 text-lg">Channel(s)</p>
          <div class="grid grid-cols-3">
            <div id="green">
              <span class="mb-1">
                <input type="checkbox" class="ml-2 mr-1 rounded text-lime-500 focus:ring-lime-300" bind:checked={cmd.laser_onoff[0]} />
                532 nm laser
                <input type="number" class="w-20 h-8 mr-1 pretty" placeholder="0" bind:value={cmd.lasers[0]} disabled={cmd.laser_onoff[0]} />
                mW
              </span>
              <ol>
                <li class="channel">
                  <input type="checkbox" class="mr-1 text-green-500 rounded focus:ring-green-300" bind:checked={cmd.channels[0]} />
                  Channel 0
                </li>
                <li class="channel">
                  <input type="checkbox" class="mr-1 text-orange-600 rounded focus:ring-orange-300" bind:checked={cmd.channels[1]} />
                  Channel 1
                </li>
              </ol>
            </div>
            <div id="red">
              <span class="mb-1">
                <input type="checkbox" class="ml-2 mr-1 text-red-600 rounded focus:ring-red-300" bind:checked={cmd.laser_onoff[1]} />
                660 nm laser
                <input type="number" class="w-20 h-8 mr-1 pretty" placeholder="0" bind:value={cmd.lasers[1]} disabled={cmd.laser_onoff[1]} />
                mW
              </span>
              <ol>
                <li class="channel">
                  <input type="checkbox" class="mr-1 rounded text-rose-700 focus:ring-rose-500" bind:checked={cmd.channels[2]} />
                  Channel 2
                </li>
                <li class="channel">
                  <input type="checkbox" class="mr-1 rounded text-amber-900 focus:ring-amber-700" bind:checked={cmd.channels[3]} />
                  Channel 3
                </li>
              </ol>
            </div>
          </div>
        </div>
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
