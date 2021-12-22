<script lang="ts">
  import { onMount } from "svelte";

  import websocketStore from "../store";
  import Main from "../components/main/main.svelte";
  import Nav from "../components/navbar/nav.svelte";
  import Sidebar from "../components/sidebar/sidebar.svelte";

  // export const myStore = websocketStore("wss://localhost:8000/ws", "a");

  // send JSON to websocket server
  // $myStore = { content: "to be saved", other_values: "all" };

  //   // receive JSON from server (push)
  //   let response = $myStore;
  let myStore;
  onMount(() => {
    myStore = websocketStore("ws://127.0.0.1:8000/ws", { a: "ourim" });
  });
</script>

<div>
  <div class="drawer drawer-mobile">
    <input id="main-menu" type="checkbox" class="drawer-toggle" />
    <main
      class="flex-grow block overflow-x-hidden bg-base-100 text-base-content drawer-content"
    >
      <Nav />
      <div class="p-4 lg:p-8"><Main /></div>
    </main>
    <Sidebar />
  </div>
</div>
