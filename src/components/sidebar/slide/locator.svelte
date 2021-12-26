<script lang="ts">
  export let x: number = 10;
  export let y: number = 10;

  let real_x: number;
  let real_y: number;
  $: {
    real_x = (100 * x) / 25;
    real_y = (100 * y) / 75;
  }
</script>

<div
  id="cross"
  class="absolute z-50 text-xl text-blue-700 transition-all"
  style="top:calc({(100 * y) / 75}% - 0.8em); right:calc({real_x}% - 0.32em);"
>
  ×
</div>

<div
  id="horz"
  class="absolute w-full border-t border-blue-200 transition-all"
  style="top:calc({real_y}% - 1px); right:0%; width:{real_x}%;"
/>
<div
  id="vert"
  class="absolute h-full border-l border-blue-200 transition-all"
  style="right:calc({real_x}% - 1px); height:{real_y}%;"
/>

<span
  id="legend"
  class="z-50 absolute font-mono font-medium text-sm text-center w-36 transition-all text-blue-700"
  style="top:calc({(100 * y) /
    75}% + 0.4rem); right:calc({real_x}% - 4.5rem); text-shadow: 0px 0px 2px white, 0px 0px 5px white, 0px 0px 10px white"
>
  ({x.toFixed(1)}, {y.toFixed(1)})
</span>
