<script lang="ts">
  import { userStore, XY } from "$src/store";

  let real_x: number;
  let real_y: number;
  $: {
    real_x = (100 * $userStore.x) / 25;
    real_y = (100 * $userStore.y) / 75;
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
