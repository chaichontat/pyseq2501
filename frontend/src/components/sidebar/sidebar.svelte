<script>
  import Division from "./division.svelte";
  import Lasers from "./lasers.svelte";
  import Logo from "./logo.svelte";
  import Map from "./map.svelte";
</script>

<div class="drawer-side">
  <label for="main-menu" class="drawer-overlay" />
  <aside class="sidebar flex flex-col bg-base-100">
    <Logo />

    <ul class="menu p-2 pt-2 compact">
      <Division name="Map">
        <Map />
      </Division>

      <Division name="Lasers">
        <Lasers />
      </Division>
    </ul>
  </aside>
</div>

<style lang="postcss">
  .sidebar {
    @apply text-base-content;
    @apply w-80 h-screen;
    @apply border-r border-base-200;
  }

  th {
    padding-left: 0.5rem;
    padding-right: 0.25rem;
    padding-top: 0.5rem;
    padding-bottom: 0.5rem;
  }
</style>
