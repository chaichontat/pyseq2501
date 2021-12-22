<script>
  import Division from "./division.svelte";
  import Lasers from "./lasers.svelte";
  import Logo from "../logo.svelte";
  import Map from "./slide/map.svelte";
</script>

<div class="drawer drawer-side">
  <label for="main-menu" class="drawer-overlay" />
  <aside class="sidebar flex flex-col bg-base-100">
    <div
      class="sticky inset-x-0 top-0 z-50 w-full py-1 transition duration-200 ease-in-out border-b block border-base-200 bg-base-100"
    >
      <Logo />
    </div>

    <ol class="menu p-2 mt-4">
      <Division name="Map">
        <Map />
      </Division>

      <Division name="Lasers">
        <Lasers />
      </Division>
    </ol>
  </aside>
</div>

<style lang="postcss">
  .sidebar {
    @apply text-base-content;
    @apply w-96 h-screen;
    @apply border-r border-base-200;
  }
</style>
