<script lang="ts">
  import { userStore as us } from "$src/stores/store";

  let real_x: [number, number];
  let real_y: [number, number];
  $: {
    real_x = [(100 * $us.image_params.xy0[0]) / 25, (100 * $us.image_params.xy1[0]) / 25];
    real_y = [(100 * $us.image_params.xy0[1]) / 75, (100 * $us.image_params.xy1[1]) / 75];
  }
</script>

<div
  class="absolute z-20 rounded-sm bg-sky-300/40 ring-2 ring-sky-200 ring-opacity-70 transition-all"
  style="
  top:calc({Math.min(...real_y)}%;
  left:calc({Math.min(...real_x)}%);
  height:{Math.max(...real_y) - Math.min(...real_y)}%;
  width:{Math.max(...real_x) - Math.min(...real_x)}%;"
/>
