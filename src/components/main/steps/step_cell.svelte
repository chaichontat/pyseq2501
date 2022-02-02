<script lang="ts">
  import Dropdown from "./dropdown.svelte";
  import type { Action } from "$src/store";
  import Setxy from "./setxy.svelte";

  export let curr: Action = "Image";
  export let n: number = 1;
</script>

<li class="relative flex py-4 pl-2 border-y border-gray-300 hover:bg-gray-50 hover:border-blue-400 transition-all ease-in-out hover:shadow-sm">
  <svg xmlns="http://www.w3.org/2000/svg" class="absolute h-5 w-5 -mt-1 right-2" viewBox="0 0 20 20" fill="currentColor">
    <path
      fill-rule="evenodd"
      d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
      clip-rule="evenodd"
    />
  </svg>

  <div class="mr-8">
    <span class="flex justify-center items-center w-14 h-14 bg-blue-100 text-lg font-bold rounded-full">{n}</span>
  </div>

  <div class="w-full mr-8">
    <Dropdown bind:curr />

    <div class="clump mt-2 grid gap-x-4 grid-cols-4 divide-x font-medium">
      <!-- Hold -->
      {#if curr === "Hold"}
        <span>
          Time <input type="number" class="mx-2 pretty w-32" placeholder="60" />
          s
        </span>
        <!-- Wash -->
      {:else if curr === "Wash"}
        <span>
          Reagent
          <select class="drop text-sm w-1/2">
            <option>1</option>
            <option>2</option>
            <option>Birthday</option>
            <option>Other</option>
          </select>
        </span>
        <span>
          Volume <input type="number" class="mx-2 pretty w-24" placeholder="2000" />
          μl
        </span>
        <!-- Prime -->
      {:else if curr === "Prime"}
        <span>
          Reagent
          <select class="drop text-sm">
            <option>Corporate event</option>
            <option>Wedding</option>
            <option>Birthday</option>
            <option>Other</option>
          </select>
        </span>
        <span>
          Volume <input type="number" class="mx-2 pretty w-24" placeholder="2000" />
          μl
        </span>
        <!-- Temp -->
      {:else if curr === "Change Temperature"}
        <span>
          Temperature <input type="number" class="mx-2 pretty w-24" placeholder="20" />
          °C
        </span>
        <!-- Move -->
      {:else if curr === "Move Stage"}
        <span>
          X <input type="number" class="mx-2 pretty w-24" placeholder="2000" />
          mm
        </span>
        <span>
          Y <input type="number" class="mx-2 pretty w-24" placeholder="2000" />
          mm
        </span>
        <!-- Image -->
      {:else if curr === "Image"}
        <span>
          Z <input type="number" class="mx-2 pretty w-24" placeholder="2000" />
        </span>
        <span>
          Autofocus <input type="checkbox" class="ml-2 rounded" />
        </span>

        <div class="col-span-4 mt-4 ml-2 pl-4">
          <p class="text-lg mb-2 gap-x-8">Lower right</p>
          <Setxy />
        </div>

        <div class="col-span-4 mt-4 ml-2 pl-4">
          <p class="text-lg mb-2">Upper left</p>
          <Setxy />
        </div>

        <!-- Channels -->
        <div class="col-span-4 mt-4 ml-2 pl-4">
          <p class="text-lg mb-2">Channel(s)</p>
          <div class="grid grid-cols-3">
            <div id="green">
              <span class="mb-1">
                <input type="checkbox" class="ml-2 mr-1 rounded text-lime-500 focus:ring-lime-300" />
                532 nm laser
                <input type="number" class="mr-1 pretty w-20 h-8" placeholder="50" />
                mW
              </span>
              <ol>
                <li class="channel">
                  <input type="checkbox" class="mr-1 rounded text-green-500 focus:ring-green-300" />
                  Channel 0
                </li>
                <li class="channel">
                  <input type="checkbox" class="mr-1 rounded text-orange-600 focus:ring-orange-300" />
                  Channel 1
                </li>
              </ol>
            </div>
            <div id="red">
              <span class="mb-1">
                <input type="checkbox" class="ml-2 mr-1 rounded text-red-600 focus:ring-red-300" />
                660 nm laser
                <input type="number" class="mr-1 pretty w-20 h-8" placeholder="50" />
                mW
              </span>
              <ol>
                <li class="channel">
                  <input type="checkbox" class="mr-1 rounded text-rose-700 focus:ring-rose-500" />
                  Channel 2
                </li>
                <li class="channel">
                  <input type="checkbox" class="mr-1 rounded text-amber-900 focus:ring-amber-700" />
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
