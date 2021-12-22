<script lang="ts">
  import RulerX from "./ruler_x.svelte";
  import RulerY from "./ruler_y.svelte";

  export let name: string = "";
</script>

<div
  class="self-center slide border border-gray-400 shadow flex relative justify-center box-border"
>
  <RulerX />
  <RulerY />

  <span class="dot left" style="top: 2rem;">
    Tilt 3 <br /> Z:
    <span>19850</span>
  </span>

  <span class="dot left" style="bottom: 2rem;">
    Tilt 2 <br /> Z:
    <span>19850</span>
  </span>

  <span class="dot right" style="bottom: 2rem; right:-7rem;">
    Tilt 1 <br /> Z:
    <span>19850</span>
  </span>

  <span class="name">
    {name}
  </span>
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
    @apply text-center font-semibold absolute top-1/3 opacity-20;
    font-size: 4rem;
  }

  .dot {
    @apply absolute text-sm;
  }
  .dot span {
    @apply font-mono;
  }

  .dot::before {
    position: absolute;
    content: "";
    clip-path: circle();
    /* transform: translateX(-1.2em) translateY(0.4em); */
    width: 1rem;
    height: 1rem;
    background: black;
    opacity: 0.5;
  }

  .left::before {
    transform: translateX(2.5rem) translateY(0.75rem);
  }

  .left {
    @apply text-right;
    left: -6.5rem;
  }

  .right {
    @apply text-left;
  }

  .right::before {
    transform: translateX(-1.5rem) translateY(0.75rem);
  }
</style>
