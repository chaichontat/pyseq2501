<script lang="ts">
  import Nav from "./nav.svelte";
  import "$src/app.css";
  import Sidebar from "./sidebar.svelte";

  import { overrideItemIdKeyNameBeforeInitialisingDndZones } from "svelte-dnd-action";
  overrideItemIdKeyNameBeforeInitialisingDndZones("uid");
</script>

<svelte:head>
  <title>PySeq 2501</title>
  <link rel="stylesheet" href="https://rsms.me/inter/inter.css" />
</svelte:head>

<div>
  <div class="drawer drawer-mobile">
    <input id="main-menu" type="checkbox" class="drawer-toggle" />
    <main class="flex-grow block overflow-x-hidden bg-white shadow-md text-base-content drawer-content">
      <Nav />
      <div class="p-4 lg:px-10">
        <slot />
      </div>
    </main>
    <Sidebar />
  </div>
</div>
