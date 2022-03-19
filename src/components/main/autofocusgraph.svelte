<script lang="ts">
  import { localStore } from "$src/stores/store";
  import * as Pancake from "@sveltejs/pancake";

  let points: { x: number; y: number }[] = [];
  export let curr = 0;

  const z_max = 60292;
  const z_min = 2621;
  const n_stack = 259;
  // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
  const real_steps = [...Array(n_stack)].map((_, i) => Math.round(z_max - ((z_max - z_min) * i) / n_stack));

  let min = 0;
  let max = 100;
  $: if ($localStore.afimg.laplacian) {
    points = $localStore.afimg.laplacian.map((v, i) => ({ x: real_steps[i], y: v }));
    min = Math.min(...$localStore.afimg.laplacian);
    min = min * 0.9;
    max = Math.max(...$localStore.afimg.laplacian, 1);
  }
</script>

<div class="chart box-border h-48 w-[400px]">
  <Pancake.Chart x1={z_min} x2={z_max} y1={min} y2={max}>
    <Pancake.Box x1={z_min} x2={z_max} y1={min} y2={max}>
      <div class="absolute h-full w-full border-b border-l border-gray-400" />
    </Pancake.Box>

    <!-- X-axis -->
    <Pancake.Grid vertical count={5} let:value>
      <div class="x label relative top-0 block h-[105%] border-r border-dashed border-r-gray-400">
        <span class="absolute -right-1 -bottom-6 text-sm text-gray-600">{value}</span>
      </div>
    </Pancake.Grid>

    <!-- Y-axis -->
    <Pancake.Grid horizontal count={3} let:value>
      <span class="absolute -left-12 text-right text-sm text-gray-600">{value}</span>
    </Pancake.Grid>

    <Pancake.Svg>
      <Pancake.SvgLine data={points} let:d>
        <path class="fill-transparent stroke-blue-300" {d} />
      </Pancake.SvgLine>
    </Pancake.Svg>

    <Pancake.Point x={points[curr].x} y={points[curr].y}>
      <span class="absolute h-3 w-3 translate-x-[-50%] translate-y-[-50%] rounded-[50%] bg-orange-400 opacity-90" />
      <!-- <div class="absolute text-sm rounded bottom-4 whitespace-nowrap" style="transform: translate(-{100 * ((points[curr].x - z_min) / (z_max - z_min))}%,0)">
        <span>{points[curr].x} years</span>
      </div> -->
    </Pancake.Point>
  </Pancake.Chart>
</div>

<style lang="postcss">
  .horizontal {
    @apply left-0 w-full border-b;
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

  path {
    stroke-linejoin: round;
    stroke-linecap: round;
  }
</style>
