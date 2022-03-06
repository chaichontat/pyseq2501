<script lang="ts">
  import { localStore } from "$src/stores/store";
  import * as Pancake from "@sveltejs/pancake";

  let points: { x: number; y: number }[] = [];
  export let curr: number = 0;

  const z_max = 60292;
  const z_min = 2621;
  const n_stack = 259;
  const real_steps = [...Array(259)].map((_, i) => Math.round(z_max - ((z_max - z_min) * i) / n_stack));

  let min = 0;
  let max = 100;
  $: if ($localStore.afimg.laplacian) {
    points = $localStore.afimg.laplacian.map((v, i) => ({ x: real_steps[i], y: v }));
    min = Math.min(...$localStore.afimg.laplacian);
    min = min * 0.9;
    max = Math.max(...$localStore.afimg.laplacian);
    console.log(points);
  }
</script>

<div class="box-border h-48 chart w-[400px]">
  <Pancake.Chart x1={z_min} x2={z_max} y1={min} y2={max}>
    <Pancake.Box x1={z_min} x2={z_max} y1={min} y2={max}>
      <div class="absolute w-full h-full border-b border-l border-gray-400" />
    </Pancake.Box>

    <!-- X-axis -->
    <Pancake.Grid vertical count={5} let:value>
      <div class="relative top-0 block border-r border-dashed h-[105%] border-r-gray-400 x label">
        <span class="absolute text-sm text-gray-600 -right-1 -bottom-6">{value}</span>
      </div>
    </Pancake.Grid>

    <!-- Y-axis -->
    <Pancake.Grid horizontal count={3} let:value>
      <span class="absolute text-sm text-right text-gray-600 -left-12">{value}</span>
    </Pancake.Grid>

    <Pancake.Svg>
      <Pancake.SvgLine data={points} let:d>
        <path class="data stroke-blue-300" {d} />
      </Pancake.SvgLine>
    </Pancake.Svg>

    <Pancake.Point x={points[curr].x} y={points[curr].y}>
      <span class="absolute translate-x-[-50%] translate-y-[-50%] rounded-[50%] bg-orange-400 w-3 h-3 opacity-90" />
      <!-- <div class="absolute text-sm rounded bottom-4 whitespace-nowrap" style="transform: translate(-{100 * ((points[curr].x - z_min) / (z_max - z_min))}%,0)">
        <span>{points[curr].x} years</span>
      </div> -->
    </Pancake.Point>
  </Pancake.Chart>
</div>

<style lang="postcss">
  .horizontal {
    @apply w-full border-b left-0;
  }

  .grid-line {
    position: relative;
    display: block;
  }

  .grid-line.vertical {
    height: calc(100%+1rem);
    border-right: 1px dashed #ccc;
  }

  .grid-line span {
    position: absolute;
    bottom: 0;
    left: 2px;
    font-family: sans-serif;
    font-size: 14px;
    color: #999;
  }

  .axes {
    @apply w-full h-full border-l border-b border-dashed border-gray-400;
  }

  .y.label {
    position: absolute;
    left: -2.5em;
    width: 2em;
    text-align: right;
    bottom: -0.5em;
  }

  .x.label {
    @apply tabular-nums;
    position: absolute;
    width: 0em;
    left: -0.5em;
    bottom: -36px;
    font-family: sans-serif;
    text-align: center;
  }

  path.data {
    stroke-linejoin: round;
    stroke-linecap: round;
    stroke-width: 2px;
    fill: none;
  }

  .annotation {
    position: absolute;
    white-space: nowrap;
    bottom: 1em;
    line-height: 1.2;
    background-color: rgba(255, 255, 255, 0.9);
    padding: 0.2em 0.4em;
    border-radius: 2px;
  }

  .annotation strong {
    display: block;
    font-size: 20px;
  }
</style>
