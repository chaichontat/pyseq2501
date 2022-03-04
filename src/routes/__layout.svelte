<script lang="ts">
  import Nav from "./nav.svelte";
  import "$src/app.css";
  import "tippy.js/dist/tippy.css";
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
    <main class="flex-grow block overflow-x-hidden overflow-y-scroll bg-white shadow-md text-base-content drawer-content">
      <Nav />
      <div class="px-10 py-4">
        <slot />
      </div>
    </main>
    <Sidebar />
  </div>
</div>

<style lang="postcss">
  :global(.tippy-box) {
    @apply text-center py-0.5 px-1 rounded-lg opacity-90;
  }

  :global(html) {
    @apply min-w-[1600px];
  }

  :global(input[type="checkbox"]) {
    @apply focus:ring-2 focus:ring-offset-0 focus:ring-opacity-50;
  }
</style>
