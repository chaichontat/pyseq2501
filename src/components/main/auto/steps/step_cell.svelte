<script lang="ts">
  import Dropdown from "./dropdown.svelte";
  import { userStore as us } from "$src/store";
  import type { Cmds } from "$src/cmds";
  import { defaults } from "$src/cmds";
  import Setxy from "./setxy.svelte";
  import { createEventDispatcher } from "svelte";

  export let n: number;
  export let cmd: Cmds;

  // Can dispatch `delete`.
  const dispatch = createEventDispatcher();

  let channels: [boolean, boolean, boolean, boolean] = [true, true, true, true];
  let laserOnOff: [boolean, boolean] = [true, true];

  function genChannelSet(cs: [boolean, boolean, boolean, boolean]): Set<0 | 1 | 2 | 3> {
    const s: Set<0 | 1 | 2 | 3> = new Set();
    for (const [i, e] of cs.entries()) {
      if (e) s.add(i as 0 | 1 | 2 | 3);
    }
    return s;
  }

  $: cmd = { ...defaults[cmd.op], ...cmd }; // Second overwrites first.
  // @ts-ignore
  $: cmd.channels = genChannelSet(channels);
  // @ts-ignore
  $: cmd.laser_onoff = laserOnOff;
</script>

<li class="relative flex py-4 pl-2 border-gray-300 transition-all ease-in-out border-y hover:bg-gray-50 hover:border-blue-400 hover:shadow-sm">
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
    <span class="items-center grid grid-cols-3">
      <div><Dropdown bind:cmd={cmd.op} /></div>
      <div class="text-lg font-medium text-gray-700">Total time: 60 s</div>
    </span>

    <div class="mt-2 font-medium grid grid-cols-4 divide-x clump gap-x-4">
      <!-- Hold -->
      {#if cmd.op === "hold"}
        <span>
          Time <input type="number" class="w-32 mx-2 pretty" placeholder="60" bind:value={cmd.time} />
          s
        </span>

        <!-- Wash -->
      {:else if cmd.op === "pump"}
        <span>
          Reagent
          <select class="text-sm drop">
            {#each $us.reagents as { id, reagent }}
              <option>{reagent.name}</option>
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
            {#each $us.reagents as { id, reagent }}
              <option>{reagent.name}</option>
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

        <!-- Move -->
      {:else if cmd.op === "move"}
        <div class="mt-4 col-span-4">
          <Setxy bind:xy={cmd.xy} />
        </div>
        <!-- Image -->
      {:else if cmd.op === "image"}
        <span>
          Z <input type="number" class="w-24 mx-2 pretty" placeholder="2000" bind:value={cmd.z_tilt} />
        </span>
        <span>
          Autofocus <input type="checkbox" class="ml-2 rounded" bind:value={cmd.autofocus} />
        </span>

        <div class="pl-4 mt-4 ml-2 col-span-4">
          <p class="mb-2 text-lg gap-x-8">Lower right</p>
          <Setxy bind:xy={cmd.xy_start} />
        </div>

        <div class="pl-4 mt-4 ml-2 col-span-4">
          <p class="mb-2 text-lg">Upper left</p>
          <Setxy bind:xy={cmd.xy_end} />
        </div>

        <!-- Channels -->
        <div class="pl-4 mt-4 ml-2 col-span-4">
          <p class="mb-2 text-lg">Channel(s)</p>
          <div class="grid grid-cols-3">
            <div id="green">
              <span class="mb-1">
                <input type="checkbox" class="ml-2 mr-1 rounded text-lime-500 focus:ring-lime-300" bind:checked={laserOnOff[0]} />
                532 nm laser
                <input type="number" class="w-20 h-8 mr-1 pretty" placeholder="0" bind:value={cmd.lasers[0]} disabled={!laserOnOff[0]} />
                mW
              </span>
              <ol>
                <li class="channel">
                  <input type="checkbox" class="mr-1 text-green-500 rounded focus:ring-green-300" bind:checked={channels[0]} />
                  Channel 0
                </li>
                <li class="channel">
                  <input type="checkbox" class="mr-1 text-orange-600 rounded focus:ring-orange-300" bind:checked={channels[1]} />
                  Channel 1
                </li>
              </ol>
            </div>
            <div id="red">
              <span class="mb-1">
                <input type="checkbox" class="ml-2 mr-1 text-red-600 rounded focus:ring-red-300" bind:checked={laserOnOff[1]} />
                660 nm laser
                <input type="number" class="w-20 h-8 mr-1 pretty" placeholder="0" bind:value={cmd.lasers[1]} disabled={!laserOnOff[1]} />
                mW
              </span>
              <ol>
                <li class="channel">
                  <input type="checkbox" class="mr-1 rounded text-rose-700 focus:ring-rose-500" bind:checked={channels[2]} />
                  Channel 2
                </li>
                <li class="channel">
                  <input type="checkbox" class="mr-1 rounded text-amber-900 focus:ring-amber-700" bind:checked={channels[3]} />
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
