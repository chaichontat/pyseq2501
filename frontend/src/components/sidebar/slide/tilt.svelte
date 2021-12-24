<script lang="ts">
  export let z_tilt: [number, number, number] = [19850, 19850, 1];
</script>

<span class="dot left" style="top: 2rem;">
  Tilt 3 <br /> Z:
  <span class="font-medium">{z_tilt[2]}</span>
</span>

<span class="dot left" style="bottom: 2rem;">
  Tilt 2 <br /> Z:
  <span class="font-medium">{z_tilt[1]}</span>
</span>

<span class="dot right" style="bottom: 2rem;">
  Tilt 1 <br /> Z:
  <span class="font-medium">{z_tilt[0]}</span>
</span>

<style lang="postcss">
  .dot {
    @apply absolute text-sm w-16;
  }

  .dot span {
    @apply font-mono;
  }

  .left::after,
  .right::before {
    position: absolute;
    content: "";
    clip-path: circle();
    /* transform: translateX(-1.2em) translateY(0.4em); */
    width: 1rem;
    height: 1rem;
    background: black;
    opacity: 0.5;
  }

  .left {
    @apply text-right float-right;
    right: 10rem;
  }

  .left::after {
    transform: translateX(0.5rem) translateY(-0.5rem);
  }

  .right {
    @apply text-left float-left;
    left: 10.5rem;
  }

  .right::before {
    transform: translateX(-1.5rem) translateY(0.75rem);
  }
</style>
