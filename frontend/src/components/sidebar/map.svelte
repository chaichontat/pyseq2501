<script>
  export let left = 100;
  export let top = 100;

  let moving = false;

  function onMouseDown() {
    moving = true;
  }

  function onMouseMove(e) {
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
  <span>
    <div class="indicator w-60 h-48 border-dark-400 border shadow-inner">
      <div
        class="indicator-item indicator-center indicator-middle badge badge-primary shadow-xl "
      />
    </div>
    <section on:mousedown={onMouseDown} style="left: {left}px; top: {top}px;" class="draggable">
      <div class="w-36 h-24 text-center align-middle text-sm bg-dark-200">
        <slot />
      </div>
    </section>
  </span>
  <!-- <div class="m-6 indicator">
    <div class="grid w-32 h-32 bg-base-300 place-items-center">content</div>
  </div> -->
</li>

<svelte:window on:mouseup={onMouseUp} on:mousemove={onMouseMove} />

<style>
  .draggable {
    user-select: none;
    cursor: move;
    border: solid 1px gray;
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
