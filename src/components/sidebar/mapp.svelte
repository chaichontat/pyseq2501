<script lang="ts">
  import { cmdStore, statusStore as ss, userStore as us } from "$src/stores/store";
  import { raw_to_local } from "../../coords";
  import BigZ from "./slide/big_z.svelte";
  import Slide from "./slide/slide.svelte";
  import Toggle from "./toggle.svelte";

  let xy = { x: 0, y: 0 };
  $: {
    xy = raw_to_local($us.image_params.fc, $ss.x, $ss.y);
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
  <span class="monomedium mb-4 flex -translate-y-6 items-center justify-center space-x-2 text-lg">
    <div class="text-gray-500 transition-all" class:text-gray-800={!$us.image_params.fc} class:font-semibold={!$us.image_params.fc}>A</div>
    <Toggle bind:checked={$us.image_params.fc} />
    <div class="text-gray-500 transition-all" class:text-gray-800={$us.image_params.fc} class:font-semibold={$us.image_params.fc}>B</div>
  </span>
  <div class="-mt-4" />
  <Slide name_={$us.image_params.fc ? "B" : "A"} x={xy.x} y={xy.y} />

  <!-- Z Objective -->
  <section class="mt-4 flex flex-grow space-x-8 self-center">
    <BigZ name_="All Tilt" value={`${($ss.z_tilt.reduce((a, b) => a + b) / $ss.z_tilt.length).toFixed(0)} ± ${(Math.max(...$ss.z_tilt) - Math.min(...$ss.z_tilt)) / 2}`} />
    <BigZ name_="Objective Z" value={$ss.z_obj} />
  </section>

  <!-- Eject button -->
  <button
    class="pretty mt-2 h-8 w-16 self-center rounded-lg border bg-gray-500 text-white shadow-md shadow-gray-300 transition-colors hover:bg-gray-600 focus:ring-gray-400 active:bg-gray-700 disabled:bg-gray-200 disabled:shadow-gray-200"
    disabled={Boolean($ss.block)}
    on:click={() => {
      $ss.block = "moving";
      // pyseq2.utils.coords.raw_to_mm(False, -6.5e6)
      $cmdStore = { move: { xy0: [0, -63.2] } };
    }}
  >
    <svg
      class="mx-auto h-4 w-4 fill-white"
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
    @apply border-2 border-red-600;
  }

  input:valid {
    @apply border;
    border-color: inherit;
  }
</style>
