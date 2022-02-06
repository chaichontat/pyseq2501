<script lang="ts">
  import Main from "./main.svelte";
  import Nav from "./nav.svelte";
  import Sidebar from "./sidebar.svelte";

  import { overrideItemIdKeyNameBeforeInitialisingDndZones } from "svelte-dnd-action";
  overrideItemIdKeyNameBeforeInitialisingDndZones("uid");
</script>

<div>
  <div class="antialiased drawer drawer-mobile">
    <input id="main-menu" type="checkbox" class="drawer-toggle" />
    <main class="flex-grow block overflow-x-hidden bg-white shadow-md text-base-content drawer-content">
      <Nav />
      <div class="p-4 lg:px-10">
        <Main />
      </div>
    </main>
    <Sidebar />
  </div>
</div>
