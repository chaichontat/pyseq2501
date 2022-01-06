<script lang="ts">
  import type { Status } from "../../store";
  import { statusStore } from "../../store";
  import Logo from "../logo.svelte";
  import Division from "./division.svelte";
  import Lasers from "./lasers.svelte";
  import Map from "./slide/map.svelte";

  let status: Status = {
    x: 2,
    y: 5,
    z_tilt: [0, 1, 2],
    z_obj: 4,
    laser_r: 3,
    laser_g: 5,
    shutter: false,
    msg: "",
  };

  let connected: boolean = false;
  // onMount(() => {
  //   const sse = new EventSource("http://localhost:8000/status");
  //   sse.onmessage = (event: MessageEvent<string>) => (status = JSON.parse(event.data));
  //   return () => {
  //     if (sse.readyState === 1) sse.close();
  //   };
  // });

  $: {
    if ($statusStore) {
      status = $statusStore;
    }
    connected = $statusStore != undefined ? true : false;
  }
</script>

<div class="drawer drawer-side">
  <label for="main-menu" class="drawer-overlay" />
  <aside class="sidebar flex flex-col overflow-y-auto bg-base-100 ">
    <div
      class="hidden lg:block sticky inset-x-0 top-0 z-40 w-full py-1 transition duration-200 ease-in-out border-b border-base-200 bg-base-100"
    >
      <Logo />
    </div>
    <div class="relative">
      <!-- <div
        class:translucent={!connected}
        class="hidden absolute w-full h-full transition-all"
      /> -->
      <ol class="menu p-2 mt-4 ">
        <Division name="Map">
          <Map {...status} />
        </Division>

        <Division name="Lasers">
          <Lasers g={status.laser_g} r={status.laser_r} />
          <li>
            <span class="self-center mt-2 text-lg">
              Shutter:&nbsp; <p class="font-mono font-bold">
                {status.shutter ? "OPENED" : "CLOSED"}
              </p>
            </span>
          </li>
        </Division>
      </ol>
    </div>
  </aside>
</div>

<style lang="postcss">
  .sidebar {
    @apply text-base-content;
    @apply w-96;
    @apply border-r border-base-200;
  }

  .translucent {
    @apply bg-white opacity-40 z-50 block;
  }
</style>
