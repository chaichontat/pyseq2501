<script lang="ts">
  import Main from "./main.svelte";
  import Nav from "./nav.svelte";
  import Sidebar from "./sidebar.svelte";
</script>

<div>
  <div class="drawer drawer-mobile antialiased">
    <input id="main-menu" type="checkbox" class="drawer-toggle" />
    <main
      class="flex-grow block overflow-x-hidden text-base-content drawer-content bg-white shadow-md"
    >
      <Nav />
      <div class="p-4 lg:px-10">
        <Main />
      </div>
    </main>
    <Sidebar />
  </div>
</div>
