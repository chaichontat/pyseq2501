<script lang="ts">
  import Slide from "./slide.svelte";
  export let left = 100;
  export let top = 100;

  let flowcell: boolean = false;

  let moving = false;

  function onMouseDown() {
    moving = true;
  }

  function onMouseMove(e: MouseEvent) {
    if (moving) {
      left += e.movementX;
      top += e.movementY;
    }
  }

  function onMouseUp() {
    moving = false;
  }

  // 	$: console.log(moving);
</script>

<li>
  <!-- Toggle -->
  <span class="monomedium justify-center align-middle mb-4 -translate-y-8">
    <div class="text-base">A</div>
    <input type="checkbox" bind:checked={flowcell} class="toggle toggle-md self-center mx-1 " />
    <div class="text-base">B</div>
  </span>
  <!-- Need this since using negative margins on the checkbox did not move the clickable area. -->
  <div class="-mt-8" />

  <!-- <div
    on:mousedown={onMouseDown}
    style="left: {left}px; top: {top}px;"
    class="indicator-item indicator-center indicator-middle badge badge-primary shadow-xl draggable z-50 opacity-70"
  /> -->

  <Slide name={flowcell ? "B" : "A"} />

  <!-- Z Objective -->
  <span class="self-center text-sm">
    Objective Z:&nbsp; <span class="font-mono font-medium">32000</span>
  </span>

  <!-- XY Input -->
  <div class="form-control self-center mt-4">
    <label class="font-medium input-group">
      <span>X</span>
      <input
        type="number"
        min="-5"
        max="30"
        step="0.01"
        class="text-lg text-center input input-bordered w-24"
      />
      <span>Y</span>
      <input
        type="number"
        min="-5"
        max="80"
        step="0.01"
        class="text-lg text-center input input-bordered w-24"
      />

      <button
        class="font-sans content-center w-12 text-indigo-100 transition-colors duration-150 bg-indigo-700 rounded-lg focus:shadow-outline hover:bg-indigo-800"
        tabindex="0"
        >Go
      </button>
    </label>
  </div>

  <!-- Eject button -->
  <button class="self-center btn btn-secondary btn-sm w-16 mt-4">
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

<svelte:window on:mouseup={onMouseUp} on:mousemove={onMouseMove} />

<style lang="postcss">
  .draggable {
    user-select: none;
    cursor: move;
    position: absolute;
  }

  .monomedium {
    @apply font-mono font-medium;
  }

  .toggle {
    --chkbg: hsla(var(--bc) / 0.2);
    --focus-shadow: 0 0 0;
    --handleoffset: 1.5rem; /* 24px */
    --tw-bg-opacity: 0.8;
    --tw-border-opacity: 0.8;
    -webkit-appearance: none;
    -moz-appearance: none;
    appearance: none;
    background-color: hsla(var(--bc) / var(--tw-bg-opacity, 1));
    border-color: hsla(var(--bc) / var(--tw-border-opacity, 1));
    border-width: 1px;
    cursor: pointer;
    height: 1.5rem; /* 24px */
    width: 3rem; /* 48px */
    transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
    transition-duration: 0.3s;
    border-radius: var(--rounded-badge, 1.9rem);
    transition: background, box-shadow var(--animation-input, 0.2s) ease-in-out;
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
    @apply border-gray-200 border;
  }
</style>
