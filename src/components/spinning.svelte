<script lang="ts">
  export let size = "1rem";
  export let color = "blue";
  export let duration = "1.5s";
</script>

<div class="circle transition-all" style="--size: {size}; --color: {color}; --duration: {duration}" />

<style>
  .circle {
    height: var(--size);
    width: var(--size);
    border-color: var(--color) transparent var(--color) var(--color);
    border-width: calc(var(--size) / 8);
    border-style: solid;
    border-image: initial;
    border-radius: 100%;
    animation: var(--duration) linear 0s infinite normal none running rotate;
  }
  @keyframes rotate {
    0% {
      transform: rotate(0);
    }
    100% {
      transform: rotate(360deg);
    }
  }
</style>
