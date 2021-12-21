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
    width: 100%;
  }

  .name {
    @apply text-center font-semibold absolute top-1/3;
    font-size: 4rem;
    opacity: 0.2;
  }
</style>
