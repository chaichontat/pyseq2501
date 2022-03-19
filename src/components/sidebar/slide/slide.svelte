<script lang="ts">
  import { userStore as us } from "$src/stores/store";
  import Locator from "./locator.svelte";
  import RulerX from "./ruler_x.svelte";
  import RulerY from "./ruler_y.svelte";
  import Shade from "./shade.svelte";
  import Tilt from "./tilt.svelte";

  export let name_ = "";
  export let x: number;
  export let y: number;

  // function handleKey(e: KeyboardEvent) {
  //   switch (e.key) {
  //     case "ArrowDown":
  //       $userStore.y += 0.7;
  //       break;

  //     case "ArrowLeft":
  //       $userStore.x -= 0.7;
  //       break;

  //     case "ArrowRight":
  //       $userStore.x += 0.7;
  //       break;

  //     case "ArrowUp":
  //       $userStore.y -= 0.7;
  //       break;

  //     default:
  //       break;
  //   }
  // }
</script>

<!-- <svelte:window on:keydown={handleKey} /> -->

<div class="bg-light-200 slide relative box-border flex justify-center self-center border border-gray-400 shadow">
  <RulerX />
  <RulerY />
  <Locator {x} {y} />
  <Locator line={false} legend={false} char="📌" x={$us.image_params.xy0[0]} y={$us.image_params.xy0[1]} offset={[0.3, 1.65]} />
  <Locator line={false} legend={false} char="📍" x={$us.image_params.xy1[0]} y={$us.image_params.xy1[1]} offset={[0.85, 1.6]} />
  <Shade />
  <Tilt />

  <span class="name">
    {name_}
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
    @apply absolute z-10 box-border w-full border-b border-gray-400;
    bottom: calc(6rem - 1px);
  }

  .name {
    @apply absolute top-1/4 text-center font-semibold opacity-20;
    font-size: 4rem;
  }
</style>
