<script lang="ts">
  import * as Pancake from "@sveltejs/pancake";
  import { imgStore } from "$src/store";

  let max: number;

  function range(a, b, step) {
    const array = [];
    for (; a <= b; a += step) array.push(a);
    return array;
  }

  function gen_xy(bin_edges: number[], counts: number[]): { x: number; y: number }[] {
    return bin_edges.map((x: number, i: number) => ({ x, y: counts[i] }));
  }

  let f: { x: number; y: number }[] = [
    { x: 0, y: 0 },
    { x: 2000, y: 10 },
  ];

  $: {
    const h = $imgStore?.hist;
    if (h) {
      console.log(h);
      f = gen_xy(h.bin_edges, h.counts);
      max = Math.max(...h.counts);
    }
  }
</script>

<div class="chart">
  <div class="foreground">
    <Pancake.Chart x1={0} x2={4096} y1={0} y2={max}>
      <Pancake.Grid horizontal count={5} let:value>
        <div class="relative block w-full left-0 border-b border-gray-100" />
        <span class="y label">{value}</span>
      </Pancake.Grid>

      <Pancake.Columns data={f} width={5}>
        <div class="column f z-10" />
      </Pancake.Columns>

      <Pancake.Grid vertical count={5} let:value>
        <span class="x label">{value}</span>
      </Pancake.Grid>
    </Pancake.Chart>
  </div>
</div>

<style lang="postcss">
  .chart {
    @apply relative h-full w-full box-border;

    /* height: 300px; */
  }

  .foreground {
    @apply absolute box-border left-8 top-4;
    height: 80%;
    width: 80%;
  }

  .horizontal {
    width: 100%;
    left: 0;
    border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  }

  .label {
    position: absolute;
    font-size: 14px;
    color: #666;
    line-height: 1;
    white-space: nowrap;
  }

  .y.label {
    left: calc(100% + 1em);
    bottom: -1em;
    line-height: 1;
  }

  .x.label {
    width: 4em;
    left: -2em;
    bottom: 5px;
    text-align: center;
  }

  .foreground .x.label {
    bottom: -36px;
  }

  .column {
    @apply absolute left-0 w-full h-full opacity-60 rounded-t-box box-border;
    border-left: 1px solid rgba(255, 255, 255, 0.4);
    border-right: 1px solid rgba(255, 255, 255, 0.4);
  }

  .column.m {
    background-color: #1f77b4;
  }

  .f {
    background-color: #e377c2;
  }

  .medium .slider-container span {
    font-size: 3.5em;
  }

  .large .slider-container span {
    font-size: 5em;
  }
</style>
