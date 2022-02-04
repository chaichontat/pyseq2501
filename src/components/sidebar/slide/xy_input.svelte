<script lang="ts">
  import Spinning from "$src/components/navbar/spinning.svelte";
  import type { XY } from "$src/store";
  import { cmdStore, userStore as user, statusStore as status } from "$src/store";
  import { local_to_raw } from "../coords";

  export let xy: XY = { x: -1, y: -1 };

  function move() {
    const raw_coord = local_to_raw($user.flowcell, $user.x, $user.y);
    $cmdStore = { cmd: "x", n: raw_coord.x };
    $cmdStore = { cmd: "y", n: raw_coord.y };
  }
</script>

<!-- XY Input -->

<div class="self-center mt-4 form-control">
  <label class="font-medium input-group">
    <span
      ><div data-tip={`${xy.x.toFixed(2)} mm`} class="tooltip tooltip-bottom">
        <b>X</b>
      </div></span
    >
    <input
      bind:value={$user.x}
      type="number"
      min="-5"
      max="30"
      step="0.01"
      class="h-10 text-lg text-center input input-bordered inputcheck w-28"
    />
    <span
      ><div data-tip={`${xy.y.toFixed(2)} mm`} class="tooltip tooltip-bottom">
        <b>Y</b>
      </div></span
    >
    <input
      bind:value={$user.y}
      type="number"
      min="-5"
      max="80"
      step="0.01"
      class="h-10 text-lg text-center input input-bordered inputcheck w-28"
    />

    <button
      class="content-center w-12 font-sans text-indigo-100 bg-indigo-700 rounded-lg transition-all duration-150 focus:shadow-outline hover:bg-indigo-800"
      tabindex="0"
      on:click={move}
    >
      {#if $status.moving}
        <div class="ml-4">
          <Spinning color="white" />
        </div>
      {:else}
        Go
      {/if}
    </button>
  </label>
</div>
