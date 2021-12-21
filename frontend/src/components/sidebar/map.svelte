<script lang="ts">
  import Slide from "./slide.svelte";
  export let left = 100;
  export let top = 100;

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
  <div
    on:mousedown={onMouseDown}
    style="left: {left}px; top: {top}px;"
    class="indicator-item indicator-center indicator-middle badge badge-primary shadow-xl draggable z-50"
  />
  <section class="flex justify-evenly divide-x divide-dashed -mt-8 -mb-4">
    <Slide name="A" />
    <Slide name="B" />
  </section>
  <input type="checkbox" class="toggle toggle-md self-center" />
  <span>
    <input type="text" class="input input-info input-bordered w-1/4" />
    <input type="text" class="input input-info input-bordered w-1/4" />
  </span>

  <!-- <section on:mousedown={onMouseDown} style="left: {left}px; top: {top}px;" class="draggable">
      <div class="w-36 h-24 text-center align-middle text-sm bg-dark-200">
        <slot />
      </div>
    </section> -->

  <!-- <div class="m-6 indicator">
    <div class="grid w-32 h-32 bg-base-300 place-items-center">content</div>
  </div> -->
</li>

<svelte:window on:mouseup={onMouseUp} on:mousemove={onMouseMove} />

<style lang="postcss">
  .draggable {
    user-select: none;
    cursor: move;
    position: absolute;
  }

  .dot {
    height: 2px;
    width: 4px;
    background-color: #000;
    border-radius: 100%;
    display: inline-block;
  }
</style>
