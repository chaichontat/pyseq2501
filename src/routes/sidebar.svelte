<script lang="ts">
  import { localStore, statusStore as ss } from "$src/stores/store";
  import Logo from "$comps/logo.svelte";
  import Division from "$src/components/sidebar/division.svelte";
  import Lasers from "$comps/sidebar/lasers.svelte";
  import Map from "$src/components/sidebar/map.svelte";
  import Modal from "$src/components/modal.svelte";
  import Preview from "$src/components/main/preview.svelte";
  import Fluidics from "$src/components/sidebar/fluidics.svelte";

  // onMount(() => {
  //   const sse = new EventSource("http://localhost:8000/status");
  //   sse.onmessage = (event: MessageEvent<string>) => (status = JSON.parse(event.data));
  //   return () => {
  //     if (sse.readyState === 1) sse.close();
  //   };
  // });

  let tab: "imaging" | "fluidics" | "misc" = "imaging";
</script>

<div class="drawer drawer-side">
  <label for="main-menu" class="drawer-overlay" />
  <aside class="flex flex-col overflow-y-auto border-r border-gray-300 w-[26rem] bg-base-100">
    <div class="sticky inset-x-0 top-0 z-40 hidden w-full h-16 transition duration-200 ease-in-out bg-white shadow-sm lg:block ring-1 ring-gray-900 ring-opacity-5">
      <Logo />
    </div>

    <div class="w-full mt-2 tabs">
      <button class="font-medium tab tab-lg tab-lifted" on:click={() => (tab = "imaging")} class:tab-active={tab === "imaging"} class:text-gray-800={tab === "imaging"}>Imaging</button>
      <button class="font-medium tab tab-lg tab-lifted" on:click={() => (tab = "fluidics")} class:tab-active={tab === "fluidics"} class:text-gray-800={tab === "fluidics"}>Fluidics</button>
      <button class="font-medium tab tab-lg tab-lifted" on:click={() => (tab = "misc")} class:tab-active={tab === "misc"} class:text-gray-800={tab === "misc"}>Misc.</button>
      <div class="flex-1 cursor-default tab tab-lifted" />
    </div>

    <section class:hidden={tab !== "imaging"} class="relative">
      <ol class="p-2 menu ">
        <Division name="Map">
          <Map />
        </Division>

        <Division name="Lasers">
          <Lasers />
          <li>
            <span class="self-center mt-2 text-lg">
              Shutter:&nbsp; <p class="font-mono font-bold">
                {$ss.shutter ? "OPENED" : "CLOSED"}
              </p>
            </span>
          </li>
        </Division>
      </ol>
    </section>

    <section class:hidden={tab !== "fluidics"} class="relative">
      <ol class="p-2 overflow-auto menu">
        <Division name="Ports">
          <Fluidics />
        </Division>
      </ol>
    </section>

    <section class:hidden={tab !== "misc"} class="relative">
      <ol class="p-2 menu ">
        <Division name="Miscellaneous">
          <div class="flex flex-col items-center gap-4 p-2">
            <button type="button" class="justify-center w-[80%] py-2 font-medium text-center text-gray-900 rounded-lg white-button" disabled={!$localStore.connected}>Reinitialize</button>
          </div>
        </Division>
      </ol>
    </section>
  </aside>
</div>
