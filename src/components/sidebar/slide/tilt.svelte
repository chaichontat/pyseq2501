<script lang="ts">
  export let z_tilt: [number, number, number] = [19850, 19850, 1];

  let editable = [false, false, false];

  import Pencil from "../../svgs/pencil.svelte";
  import Editable from "./editable.svelte";

  $: console.log(editable);
</script>

<div class="dot left top-8">
  <div>
    Tilt 3<Editable
      bind:editable={editable[2]}
      value={z_tilt[2]}
      clDisp="absolute right-8 leading-6 font-mono font-medium"
      clInp="absolute text-base top-5 right-6 input input-smaller w-16 text-right"
    />
  </div>
  <Pencil class="ml-2" on:click={() => (editable[2] = true)} />
</div>

<span class="dot left" style="top: 19rem;">
  <div>
    Tilt 2<Editable
      bind:editable={editable[1]}
      value={z_tilt[1]}
      clDisp="absolute right-8 leading-6 font-mono font-medium"
      clInp="absolute text-base top-5 right-6 input input-smaller w-16 text-right"
    />
  </div>
  <Pencil class="ml-2" on:click={() => (editable[1] = true)} />
</span>

<span class="dot right">
  <Pencil class="mr-2" on:click={() => (editable[0] = true)} />
  <div>
    Tilt 1
    <Editable
      bind:editable={editable[0]}
      value={z_tilt[0]}
      clDisp="absolute left-6 leading-6 font-mono font-medium"
      clInp="absolute top-5 left-4 text-base input input-smaller w-16"
    />
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

  .right {
    top: 19rem;
    left: 9.5rem;
  }

  .left {
    @apply text-right float-right right-32;
  }
</style>
