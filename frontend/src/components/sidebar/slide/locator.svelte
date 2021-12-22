<script lang="ts">
  export let x: number = 10;
  export let y: number = 10;

  let real_x: number;
  let real_y: number;
  $: {
    real_x = (100 * x) / 25;
    real_y = (100 * x) / 75;
  }
</script>

<div
  class="absolute z-50 text-xl text-blue-700"
  style="top:calc({(100 * y) / 75}% - 0.8em); right:calc({real_x}% - 0.32em);"
>
  ×
</div>

<div
  class="absolute w-full border-t border-gray-400"
  style="top:calc({real_y}% - 1px); right:0%; width:{real_x}%;"
/>
<div
  class="absolute h-full border-l border-gray-400"
  style="right:calc({real_x}% - 1px); height:{real_y}%;"
/>

<span
  class="absolute font-mono font-medium text-sm text-center w-36"
  style="top:calc({(100 * y) /
    75}% + 0.6em); right:calc({real_x}% - 4.5rem); text-shadow: 2px 2px 8px white;"
>
  ({x.toFixed(1)}, {y.toFixed(1)})
</span>
