<script lang="ts">
  import * as Pancake from "@sveltejs/pancake";
  const points = [
    { x: 0, y: 0 },
    { x: 1, y: 1 },
    { x: 2, y: 4 },
    { x: 3, y: 9 },
    { x: 4, y: 16 },
    { x: 5, y: 25 },
    { x: 6, y: 36 },
    { x: 7, y: 49 },
    { x: 8, y: 64 },
    { x: 9, y: 81 },
    { x: 10, y: 100 },
  ];
</script>

<div class="w-96 h-48 box-border chart">
  <Pancake.Chart x1={0} x2={10} y1={0} y2={100}>
    <Pancake.Box x2={10} y2={100}>
      <div class="axes" />
    </Pancake.Box>

    <Pancake.Grid vertical count={5} let:value>
      <!-- <span class="x label">{value}</span> -->
      <div class="grid-line vertical x label"><span>{value}</span></div>
    </Pancake.Grid>

    <Pancake.Grid horizontal count={3} let:value>
      <span class="y label">{value}</span>
    </Pancake.Grid>

    <Pancake.Svg>
      <Pancake.SvgLine data={points} let:d>
        <path class="data stroke-blue-300" {d} />
      </Pancake.SvgLine>
    </Pancake.Svg>
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
</style>
