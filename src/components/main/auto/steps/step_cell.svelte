<script lang="ts">
  import Takeimage from "$src/components/main/takeimage/takeimage.svelte";
  import Modal from "$src/components/modal.svelte";
  import type { Cmd, Ops } from "$src/stores/command";
  import { userStore as us } from "$src/stores/store";
  import { checkRange } from "$src/utils";
  import { createEventDispatcher } from "svelte";
  import Preview from "../../preview.svelte";
  import Dropdown from "./dropdown.svelte";
  export let n: number;
  export let cmd: Cmd;

  export let fc_: 0 | 1;

  // Can dispatch `delete`.
  const dispatch = createEventDispatcher();

  const borderColor: { [key in Ops]: string } = {
    pump: "border-blue-300",
    prime: "border-sky-300",
    takeimage: "border-red-300",
    hold: "border-green-300",
    temp: "border-teal-300",
    autofocus: "border-orange-300",
    goto: "border-red-300",
  };
</script>

<li class={`relative flex border-t-2 py-4 pb-6 pl-2 transition-all ease-in-out hover:bg-gray-50 ${borderColor[cmd.op]}`}>
  <!-- Close -->
  <svg xmlns="http://www.w3.org/2000/svg" class="absolute right-2 -mt-1 h-5 w-5 cursor-pointer" viewBox="0 0 20 20" fill="currentColor" on:click={() => dispatch("delete")}>
    <path
      fill-rule="evenodd"
      d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
      clip-rule="evenodd"
    />
  </svg>

  <!-- n -->
  <div class="mr-8">
    <span class="flex h-14 w-14 items-center justify-center rounded-full bg-blue-100 text-lg font-bold">
      <div>{n}</div>
    </span>
  </div>

  <div class="mr-8 w-full">
    <span class="flex items-center gap-x-16">
      <div><Dropdown bind:cmd /></div>

      <!-- Hold -->
      {#if cmd.op === "hold"}
        <p>
          Time <input type="number" class="pretty ml-3 mr-1 w-16 py-1 font-medium" bind:value={cmd.time} use:checkRange={[0, 99]} min="0" max="99" />
          h
          <input type="number" class="pretty ml-3 mr-1 w-16 py-1 font-medium" bind:value={cmd.time} use:checkRange={[0, 59]} min="0" max="59" />
          m
          <input type="number" class="pretty ml-3 mr-1 w-16 py-1 font-medium" bind:value={cmd.time} use:checkRange={[0, 59]} min="0" max="59" />
          s
        </p>

        <!--  Goto considered harmful -->
      {:else if cmd.op === "goto"}
        <p>
          Go to <input type="number" class="w-16 py-1 mx-2 font-medium pretty" bind:value={cmd.step} use:checkRange={[1, n]} min="1" max={n} />
          for
          <input type="number" class="w-16 py-1 mx-2 font-medium pretty" bind:value={cmd.n} use:checkRange={[1, Infinity]} min="1" />
          times.
        </p>

        <!-- Wash -->
      {:else if cmd.op === "pump"}
        <p>
          <span>
            Reagent
            <select class="mx-2 pretty">
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
            Volume <input type="number" class="w-24 py-1 mx-2 font-medium pretty" use:checkRange={[1, 2000]} min="1" max="2000" bind:value={cmd.volume} />
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
            Volume <input type="number" class="w-24 py-1 mx-2 font-medium pretty" use:checkRange={[1, 2000]} min="1" max="2000" bind:value={cmd.volume} />
            μl
          </span>
        </p>
        <!-- Temp -->
      {:else if cmd.op === "temp"}
        <p>
          Temperature <input type="number" class="w-24 py-1 mx-2 font-medium pretty" use:checkRange={[10, 60]} min="10" max="60" bind:value={cmd.temp} />
          °C
        </p>
        <!-- Image -->
      {:else if cmd.op === "takeimage"}
        <Modal>
          <button slot="button" type="button" class="h-10 px-4 py-2 mt-2 font-medium text-gray-800 rounded-lg white-button">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>

            <span>Show Preview</span>
          </button>
          <Preview />
        </Modal>
      {/if}
    </span>

    <!-- <span class="ml-6 text-lg font-medium text-gray-600 ">
      Time: <div class="inline-block font-mono text-xl text-gray-700 whitespace-nowrap">60</div>
      s
    </span> -->

    <!-- Those that require more space. -->
    {#if cmd.op === "takeimage"}
      <div class="clump mt-2 grid grid-cols-4 gap-x-4 divide-x font-medium">
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
    @apply text-lg font-medium;
  }

  .minor-box {
    @apply mx-2 w-24 py-1;
  }
</style>
