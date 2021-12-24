<script lang="ts">
  import Locator from "./locator.svelte";

  import RulerX from "./ruler_x.svelte";
  import RulerY from "./ruler_y.svelte";
  import Tilt from "./tilt.svelte";

  export let name: string = "";
  export let x = 0;
  export let y = 0;
  export let z_tilt: [number, number, number] = [19850, 19850, 19850];
</script>

<div
  class="bg-light-200 self-center slide border border-gray-400 shadow flex relative justify-center box-border"
>
  <RulerX />
  <RulerY />
  <Locator {x} {y} />
  <Tilt {z_tilt} />

  <span class="name">
    {name}
  </span>

  <!-- White part of the slide -->
  <div class="label-line" />
</div>

<style lang="postcss">
  .slide {
    width: 7.5rem;
    height: 22.5rem;
  }

  .label-line {
    @apply absolute border-b border-gray-400 w-full box-border;
    bottom: calc(6rem - 1px);
  }

  .name {
    @apply text-center font-semibold absolute top-1/4 opacity-20;
    font-size: 4rem;
  }
</style>
