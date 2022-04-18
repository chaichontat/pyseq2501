<script lang="ts">
  export let x: number;
  export let y: number;
  export let line = true;
  export let legend = true;
  export let char = "×";
  export let offset: [number, number] = [0.5, 1.2];

  let real_x: number;
  let real_y: number;

  $: {
    real_x = (100 * x) / 25;
    real_y = (100 * y) / 75;
  }
</script>

<div id="cross" class="absolute z-40 text-2xl text-blue-700 transition-all" style="top:calc({real_y}% - {offset[1]}rem); left:calc({real_x}% - {offset[0]}rem);">
  {char}
</div>

{#if line}
  {#if y >= 0 && y <= 75}
    <div id="horz" class="absolute z-30 w-full border-t border-blue-200 transition-all" style="top:calc({real_y}% - 1px); right:{25 - x > 0 ? 0 : 100 - real_x}%; width:{Math.abs(100 - real_x)}%;" />
  {/if}
  {#if x >= 0 && x <= 25}
    <div id="vert" class="absolute z-30 h-full border-l border-blue-200 transition-all" style="top:{real_y > 0 ? 0 : real_y}%; left:calc({real_x}% - 1px); height:{Math.abs(real_y)}%;" />
  {/if}
{/if}

{#if legend}
  <span
    id="legend"
    class="absolute z-20 w-36 text-center font-mono font-bold text-blue-700 transition-all"
    style="top:calc({(100 * y) / 75}% + 0.6rem); left:calc({real_x}% - 4.5rem); text-shadow: 0px 0px 2px white, 0px 0px 5px white, 0px 0px 10px white"
  >
    ({x.toFixed(1)}, {y.toFixed(1)})
  </span>
{/if}
