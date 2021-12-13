<script>
  import Division from "./division.svelte";
  import Laser from "./laser.svelte";
  import Logo from "./logo.svelte";
  import Map from "./map.svelte";
</script>

<div class="drawer-side">
  <label for="main-menu" class="drawer-overlay" />
  <aside
    class="flex flex-col justify-between border-r border-base-200 bg-base-100 text-base-content w-80 h-screen"
  >
    <Logo />

    <ul class="menu flex flex-col p-4 pt-2 compact">
      <Division name="Map">
        <Map>
          <h1>Stage Drag me</h1>
        </Map>
      </Division>
      <Division name="Lasers">
        <Laser desc="532 nm" color="180 100% 29%" />
        <Laser desc="633 nm" color="var(--er)" />
      </Division>

      <Division name="Stage">
        <Laser desc="X" color="var(--er)" />
      </Division>

      <li />
    </ul>
  </aside>
</div>
