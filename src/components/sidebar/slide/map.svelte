<script lang="ts">
  import type { XY } from "src/store";
  import BigZ from "./big_z.svelte";
  import Slide from "./slide.svelte";
  import XYInput from "./xy_input.svelte";
  import { statusStore as store } from "$src/store";
  export let x = 10;
  export let y = 10;
  export let z_tilt: [number, number, number] = [0, 0, 0];
  export let z_obj = 0;

  const Y_UPPER = -180000;
  const Y_STEP_MM = 1e5;
  const X_STEP_MM = 409.6;
  const A_LEFT = 7331;
  const B_LEFT = 33070;

  export let xy_user: XY = { x: 2, y: 2 };

  let flowcell: boolean = false;

  const focus = (el) => {
    el.focus;
  };

  let xy: XY = { x: $store.x, y: $store.y };
  let x_offset = A_LEFT;
  $: {
    x_offset = flowcell ? B_LEFT : A_LEFT;
    xy = {
      x: ($store.x - x_offset) / X_STEP_MM,
      y: ($store.y - Y_UPPER) / Y_STEP_MM,
    };
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
  <span class="monomedium justify-center align-middle mb-4 -translate-y-8">
    <div class="text-base">A</div>
    <input
      type="checkbox"
      bind:checked={flowcell}
      class="toggle toggle-md toggl-dark self-center mx-1"
    />
    <div class="text-base">B</div>
  </span>
  <!-- Need this since using negative margins on the checkbox did not move the clickable area. -->
  <div class="-mt-8" />

  <!-- <div
    on:mousedown={onMouseDown}
    style="left: {left}px; top: {top}px;"
    class="indicator-item indicator-center indicator-middle badge badge-primary shadow-xl draggable z-50 opacity-70"
  /> -->

  <Slide name={flowcell ? "B" : "A"} {xy} {xy_user} {z_tilt} />

  <!-- Z Objective -->
  <section class="flex flex-grow space-x-8 self-center mt-4">
    <BigZ name="All Tilt" />
    <BigZ name="Objective Z" />
  </section>

  <XYInput bind:xy_user bind:xy />

  <!-- Eject button -->
  <button class="self-center btn btn-secondary btn-sm w-16 mt-2">
    <svg
      class="w-4 h-4 fill-current "
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
