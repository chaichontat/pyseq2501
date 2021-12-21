<script lang="ts">
  export let name: string = "";
</script>

<div class="p-4 pt-8 pb-8 border-gray-400">
  <div class="slide border border-gray-400 shadow flex relative justify-center">
    <span class="name">
      {name}
    </span>
    <div class="label-line" />
  </div>
</div>

<style lang="postcss">
  .slide {
    width: 7.5rem;
    height: 22.5rem;
  }

  .label-line {
    @apply absolute border-b border-gray-400 w-full;
    bottom: 6rem;
    width: 100%;
  }

  .name {
    @apply text-center font-semibold absolute top-1/3;
    font-size: 4rem;
    opacity: 0.2;
  }
</style>
