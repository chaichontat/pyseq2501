<script>
  import Division from "./division.svelte";
  import Laser from "./laser.svelte";
  import Logo from "./logo.svelte";
  import Map from "./map.svelte";
</script>

<div class="drawer-side">
  <label for="main-menu" class="drawer-overlay" />
  <aside class="sidebar flex flex-col bg-base-100">
    <Logo />

    <ul class="menu p-4 pt-2 compact">
      <Division name="Map">
        <Map>
          <h1>Stage Drag me</h1>
        </Map>
      </Division>

      <Division name="Lasers">
        <li>
          <table class="table w-full text-sm table-fixed" style="margin-top:-0.5rem;">
            <colgroup>
              <col style="width:30%" />
              <col style="width:30%" />
              <col style="width:28%" />
              <col style="width:12%" />
            </colgroup>
            <thead class="text-right">
              <tr>
                <th />
                <th class="text-right" style="padding-right:0.3rem;">Target</th>
                <th>Actual</th>
                <th />
              </tr>
            </thead>
            <tbody>
              <Laser name="532 nm" color="#84cc16" />
              <Laser name="633 nm" color="#ef4444" />
            </tbody>
          </table>
        </li>
      </Division>

      <Division name="Stage" />
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
