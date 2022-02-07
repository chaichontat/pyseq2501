<script lang="ts">
  import type { XY } from "src/store";
  import BigZ from "./slide/big_z.svelte";
  import Slide from "./slide/slide.svelte";
  import XYInput from "./slide/xy_input.svelte";
  import { statusStore as store, userStore as us } from "$src/store";
  import { raw_to_local } from "./coords";

  const focus = (el) => {
    el.focus;
  };

  let xy: XY = { x: 0, y: 0 };
  $: {
    xy = raw_to_local($us.flowcell, $store.x, $store.y);
  }

  // let moving = false;

  // function onMouseDown() {
  //   moving = true;
  // }

  // function onMouseMove(e: MouseEvent) {
  //   if (moving) {
  //     left += e.movementX;
  //     top += e.movementY;
  //   }
  // }

  // function onMouseUp() {
  //   moving = false;
  // }
</script>

<li>
  <!-- Toggle -->
  <span class="justify-center mb-4 align-middle -translate-y-8 monomedium">
    <div class="text-base">A</div>
    <input
      type="checkbox"
      bind:checked={$us.flowcell}
      class="self-center mx-1 toggle toggle-md toggl-dark"
      class:opacity-40={$us.mode.startsWith("editing")}
      disabled={$us.mode.startsWith("editing")}
    />
    <div class="text-base">B</div>
  </span>
  <!-- Need this since using negative margins on the checkbox did not move the clickable area. -->
  <div class="-mt-8" />

  <!-- <div
    on:mousedown={onMouseDown}
    style="left: {left}px; top: {top}px;"
    class="z-50 shadow-xl indicator-item indicator-center indicator-middle badge badge-primary draggable opacity-70"
  /> -->

  <Slide name={$us.flowcell ? "B" : "A"} x={xy.x} y={xy.y} z_tilt={$store.z_tilt} />

  <!-- Z Objective -->
  <section class="flex self-center flex-grow mt-4 space-x-8">
    <BigZ name="All Tilt" value={`${$store.z_tilt.reduce((a, b) => a + b) / $store.z_tilt.length} ± ${(Math.max(...$store.z_tilt) - Math.min(...$store.z_tilt)) / 2}`} />
    <BigZ name="Objective Z" value={$store.z_obj} bind:userValue={$us.z_obj} />
  </section>

  <XYInput {xy} />
</li>

<!-- <svelte:window on:mouseup={onMouseUp} on:mousemove={onMouseMove} /> -->
<style lang="postcss">
  /* .draggable {
    user-select: none;
    cursor: move;
    position: absolute;
  } */

  .monomedium {
    @apply font-mono font-medium;
  }

  .toggl-dark {
    --tw-bg-opacity: 0.8;
  }

  /* Remove arrows
  input::-webkit-outer-spin-button,
  input::-webkit-inner-spin-button {
    -webkit-appearance: none;
    margin: 0;
  }
  input[type="number"] {
    -moz-appearance: textfield;
  } */

  input:invalid {
    @apply border-red-600 border-2;
  }

  input:valid {
    @apply border;
    border-color: inherit;
  }
</style>
