<script lang="ts">
  export let z: [number, number, number] = [-1, -1, -1];
  export let user_z: number | [number, number, number] = [-1, -1, -1];

  let editing = [false, false, false];

  import Pencil from "../../svgs/pencil.svelte";
  import Editable from "./editable.svelte";
</script>

<div class="dot left top-8">
  <div>
    Tilt 3<Editable bind:editing={editing[2]} value={z[2]} clDisp="absolute right-8 leading-6 font-mono font-medium" clInp="absolute text-base top-5 right-6 input input-smaller w-16 text-right" />
  </div>
  <Pencil class="ml-2" on:click={() => (editing[2] = true)} />
</div>

<span class="dot left" style="top: 19rem;">
  <div>
    Tilt 2<Editable bind:editing={editing[1]} value={z[1]} clDisp="absolute right-8 leading-6 font-mono font-medium" clInp="absolute text-base top-5 right-6 input input-smaller w-16 text-right" />
  </div>
  <Pencil class="ml-2" on:click={() => (editing[1] = true)} />
</span>

<span class="dot right">
  <Pencil class="mr-2" on:click={() => (editing[0] = true)} />
  <div>
    Tilt 1
    <Editable bind:editing={editing[0]} value={z[0]} clDisp="absolute left-6 leading-6 font-mono font-medium" clInp="absolute top-5 left-4 text-base input input-smaller w-16" />
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
