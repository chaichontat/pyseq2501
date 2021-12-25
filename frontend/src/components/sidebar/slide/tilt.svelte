<script lang="ts">
  export let z_tilt: [number, number, number] = [19850, 19850, 1];

  import Pencil from "../../svgs/pencil.svelte";
</script>

<span class="dot left top-8">
  <div>
    Tilt 3 <br /> Z:&nbsp;<span class="font-medium">{z_tilt[2]}</span>
  </div>
  <Pencil class="ml-2" />
</span>

<span class="dot left bottom-8">
  <div>
    Tilt 2 <br /> Z:&nbsp;<span class="font-medium">{z_tilt[1]}</span>
  </div>
  <Pencil class="ml-2" />
</span>

<span class="dot bottom-8 left-36">
  <Pencil class="mr-2" />
  <div>
    Tilt 1 <br /> Z:&nbsp;<span class="font-medium">{z_tilt[0]}</span>
  </div>
</span>

<style lang="postcss">
  .dot {
    @apply absolute flex text-sm w-16;
  }

  .dot span {
    @apply font-mono;
  }

  /* .left::after,
  .right::before {
    position: absolute;
    content: "";
    clip-path: circle();
     transform: translateX(-1.2em) translateY(0.4em);
    width: 1rem;
    height: 1rem;
    background: black;
    opacity: 0.5;
  */

  .left {
    @apply text-right float-right right-32;
  }
</style>
