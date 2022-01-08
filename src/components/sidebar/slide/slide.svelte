<script lang="ts">
  import type { XY } from "src/store";
  import { userStore, statusStore } from "$src/store";
  import Locator from "./locator.svelte";
  import RulerX from "./ruler_x.svelte";
  import RulerY from "./ruler_y.svelte";
  import Shade from "./shade.svelte";
  import Tilt from "./tilt.svelte";

  export let name: string = "";
  export let x;
  export let y;
  export let z_tilt: [number, number, number] = [19850, 19850, 19850];

  function handleKey(e: KeyboardEvent) {
    console.log(e);
    switch (e.key) {
      case "ArrowDown":
        $userStore.y += 0.7;
        break;

      case "ArrowLeft":
        $userStore.x -= 0.7;
        break;

      case "ArrowRight":
        $userStore.x += 0.7;
        break;

      case "ArrowUp":
        $userStore.y -= 0.7;
        break;

      default:
        break;
    }
  }
</script>

<svelte:window on:keydown={handleKey} />

<div
  class="bg-light-200 self-center slide border border-gray-400 shadow flex relative justify-center box-border"
>
  <RulerX />
  <RulerY />
  <Locator {x} {y} />
  <Locator
    line={false}
    legend={false}
    char="📍"
    x={$userStore.x}
    y={$userStore.y}
    offset={[0.8, 1.65]}
  />
  <Shade />
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
    @apply absolute border-b border-gray-400 w-full box-border z-10;
    bottom: calc(6rem - 1px);
  }

  .name {
    @apply text-center font-semibold absolute top-1/4 opacity-20;
    font-size: 4rem;
  }
</style>
