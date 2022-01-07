<script lang="ts">
  import { userStore, XY } from "$src/store";

  export let xy: XY = { x: 0, y: 0 };

  let real_x: number;
  let real_y: number;
  let x = xy.x;
  let y = xy.y;
  $: {
    x = xy.x;
    y = xy.y;
    real_x = (100 * x) / 25;
    real_y = (100 * y) / 75;
  }
</script>

<div
  id="shade"
  class="absolute z-20 transition-all"
  style="
  bottom:calc({100 - real_y}%;
  left:calc({real_x}%);
  height:{(100 * 0.048 * $userStore.n) / 75}%;
  width:{(100 * 0.768) / 25}%;"
/>

<style lang="postcss">
  #shade {
    @apply opacity-60;
    background-color: black;
  }
</style>
