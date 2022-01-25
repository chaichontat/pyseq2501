<script lang="ts">
  import type { Status } from "$src/store";
  import { statusStore } from "$src/store";
  import Logo from "$comps/logo.svelte";
  import Division from "$comps/sidebar/division.svelte";
  import Lasers from "$comps/sidebar/lasers.svelte";
  import Map from "$src/components/sidebar/map.svelte";

  let connected: boolean = false;
  // onMount(() => {
  //   const sse = new EventSource("http://localhost:8000/status");
  //   sse.onmessage = (event: MessageEvent<string>) => (status = JSON.parse(event.data));
  //   return () => {
  //     if (sse.readyState === 1) sse.close();
  //   };
  // });
  let status: Status = $statusStore;
  let curr: "imaging" | "fluidics" | "misc" = "imaging";

  $: {
    status = $statusStore;
    connected = $statusStore != undefined ? true : false;
  }
  $: console.log(curr);
</script>

<div class="drawer drawer-side">
  <label for="main-menu" class="drawer-overlay" />
  <aside class="sidebar flex flex-col overflow-y-auto bg-base-100">
    <div
      class="hidden lg:block sticky inset-x-0 top-0 z-40 w-full py-1 transition duration-200 ease-in-out ring-1 ring-gray-900 ring-opacity-5 shadow-sm bg-white"
    >
      <Logo />
    </div>

    <div class="tabs w-full mt-2">
      <a
        class="tab tab-lg tab-lifted"
        on:click={() => (curr = "imaging")}
        class:tab-active={curr === "imaging"}>Imaging</a
      >
      <a
        class="tab tab-lg tab-lifted"
        on:click={() => (curr = "fluidics")}
        class:tab-active={curr === "fluidics"}>Fluidics</a
      >
      <a
        class="tab tab-lg tab-lifted"
        on:click={() => (curr = "misc")}
        class:tab-active={curr === "misc"}>Misc.</a
      >
      <div class="flex-1 cursor-default tab tab-lifted" />
    </div>

    <section class:hidden={curr !== "imaging"} class="relative">
      <!-- <div
        class:translucent={!connected}
        class="hidden absolute w-full h-full transition-all"
      /> -->
      <ol class="menu p-2 ">
        <Division name="Map">
          <Map {...status} />
        </Division>

        <Division name="Lasers">
          <Lasers />
          <li>
            <span class="self-center mt-2 text-lg">
              Shutter:&nbsp; <p class="font-mono font-bold">
                {status.shutter ? "OPENED" : "CLOSED"}
              </p>
            </span>
          </li>
        </Division>
      </ol>
    </section>

    <section class:hidden={curr !== "fluidics"} class="relative">
      <ol class="menu p-2 ">
        <Division name="Prime">Drop selection port volume speed up down</Division>
      </ol>
    </section>
  </aside>
</div>

<style lang="postcss">
  .sidebar {
    @apply text-base-content;
    @apply border-r border-base-200;
    width: 26rem;
  }

  .translucent {
    @apply bg-white opacity-40 z-50 block;
  }

  .circle {
    background: #456bd9;
    border: 0.1875em solid #0f1c3f;
    border-radius: 50%;
    box-shadow: 0.375em 0.375em 0 0 rgba(15, 28, 63, 0.125);
    height: 5em;
    width: 5em;
  }
</style>
