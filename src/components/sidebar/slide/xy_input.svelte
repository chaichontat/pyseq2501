<script lang="ts">
  import Spinning from "$src/components/navbar/spinning.svelte";
  import type { XY } from "$src/store";
  import { cmdStore, userStore as us, statusStore as status } from "$src/store";
  import { local_to_raw } from "../coords";

  export let xy: XY = { x: -1, y: -1 };

  function move() {
    const raw_coord = local_to_raw($us.flowcell, $us.x, $us.y);
    $cmdStore = { cmd: "x", n: raw_coord.x };
    $cmdStore = { cmd: "y", n: raw_coord.y };
  }
</script>

<!-- XY Input -->
{#if $us.mode === "manual"}
  <div class="self-center mt-4 form-control">
    <label class="font-medium input-group">
      <span>
        <div data-tip={`${xy.x.toFixed(2)} mm`} class="tooltip tooltip-bottom">
          <b>X</b>
        </div>
      </span>
      <input bind:value={$us.x} type="number" min="-5" max="30" step="0.01" class="h-10 text-lg text-center input input-bordered inputcheck w-28" />
      <span>
        <div data-tip={`${xy.y.toFixed(2)} mm`} class="tooltip tooltip-bottom">
          <b>Y</b>
        </div>
      </span>
      <input bind:value={$us.y} type="number" min="-5" max="80" step="0.01" class="h-10 text-lg text-center input input-bordered inputcheck w-28" />

      <button class="content-center w-12 font-sans text-indigo-100 transition-all duration-150 bg-indigo-700 rounded-lg focus:shadow-outline hover:bg-indigo-800" tabindex="0" on:click={move}>
        {#if $status.moving}
          <div class="ml-4">
            <Spinning color="white" />
          </div>
        {:else}
          Go
        {/if}
      </button>
    </label>

    <!-- Eject button -->
    <button class="self-center w-16 h-8 mt-2 text-white transition-colors bg-indigo-500 pretty hover:bg-indigo-600 active:bg-indigo-700">
      <svg
        class="w-4 h-4 mx-auto -translate-x-0.5 fill-current"
        version="1.1"
        viewBox="0 0 300.02 300.02"
        style="enable-background:new 0 0 300.02 300.02; border-top-right-radius:initial; border-bottom-right-radius:initial;"
        xml:space="preserve"
      >
        <path
          d="M285,260.01H15c-8.284,0-15,6.716-15,15s6.716,15,15,15h270c8.284,0,15-6.716,15-15
            S293.284,260.01,285,260.01z"
        />
        <path
          d="M15,210.01h270c0.006-0.001,0.013-0.001,0.02,0c8.284,0,15-6.716,15-15c0-3.774-1.394-7.223-3.695-9.859
            L161.747,15.682c-2.845-3.583-7.171-5.672-11.747-5.672c-4.576,0-8.901,2.088-11.747,5.672l-135,170
            c-3.58,4.508-4.264,10.667-1.761,15.85C3.995,206.716,9.244,210.01,15,210.01z M150,49.13l103.934,130.88H46.066L150,49.13z"
        />
      </svg>
    </button>
  </div>
{/if}
