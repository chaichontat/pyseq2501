<script lang="ts">
  import { localStore, statusStore as ss } from "$src/stores/store";
  import Logo from "$comps/logo.svelte";
  import Division from "$src/components/sidebar/division.svelte";
  import Lasers from "$comps/sidebar/lasers.svelte";
  import Mapp from "$src/components/sidebar/mapp.svelte";
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
  <aside class="flex w-[26rem] flex-col overflow-y-auto border-r border-gray-300 bg-base-100">
    <div class="sticky inset-x-0 top-0 z-40 hidden h-16 w-full bg-white shadow-sm ring-1 ring-gray-900 ring-opacity-5 transition duration-200 ease-in-out lg:block">
      <Logo />
    </div>

    <div class="tabs mt-2 w-full">
      <button class="tab tab-lifted tab-lg font-medium" on:click={() => (tab = "imaging")} class:tab-active={tab === "imaging"} class:text-gray-800={tab === "imaging"}>Imaging</button>
      <button class="tab tab-lifted tab-lg font-medium" on:click={() => (tab = "fluidics")} class:tab-active={tab === "fluidics"} class:text-gray-800={tab === "fluidics"}>Fluidics</button>
      <button class="tab tab-lifted tab-lg font-medium" on:click={() => (tab = "misc")} class:tab-active={tab === "misc"} class:text-gray-800={tab === "misc"}>Misc.</button>
      <div class="tab tab-lifted flex-1 cursor-default" />
    </div>

    <section class:hidden={tab !== "imaging"} class="relative">
      <ol class="menu p-2 ">
        <Division name_="Map">
          <Mapp />
        </Division>

        <Division name_="Lasers">
          <Lasers />
          <li>
            <span class="mt-2 self-center text-lg">
              Shutter:&nbsp; <p class="font-mono font-bold">
                {$ss.shutter ? "OPENED" : "CLOSED"}
              </p>
            </span>
          </li>
        </Division>
      </ol>
    </section>

    <section class:hidden={tab !== "fluidics"} class="relative">
      <ol class="menu overflow-auto p-2">
        <Division name_="Ports">
          <Fluidics />
        </Division>
      </ol>
    </section>

    <section class:hidden={tab !== "misc"} class="relative">
      <ol class="menu p-2 ">
        <Division name_="Miscellaneous">
          <div class="flex flex-col items-center gap-4 p-2">
            <button type="button" class="white-button w-[80%] justify-center rounded-lg py-2 text-center font-medium text-gray-900" disabled={!$localStore.connected}>Reinitialize</button>
          </div>
        </Division>
      </ol>
    </section>
  </aside>
</div>
