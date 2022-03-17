<script lang="ts">
  import type { Cmd, Ops } from "$src/stores/command";
  import { cmdDefaults } from "$src/stores/command";
  import { Menu, MenuButton, MenuItem, MenuItems } from "@rgossiaux/svelte-headlessui";
  import { cubicInOut } from "svelte/easing";
  import { fade } from "svelte/transition";
  export let cmd: Cmd = { ...cmdDefaults.pump };
  const namemap: Record<Ops, string> = {
    autofocus: "Autofocus",
    pump: "Pump",
    prime: "Prime",
    temp: "Change Temperature",
    hold: "Hold",
    takeimage: "Image",
    goto: "Go to",
  };

  function handleClick(target: Ops) {
    return () => {
      cmd = { ...cmdDefaults[target] };
    };
  }
</script>

<Menu class="relative inline-block text-left">
  <MenuButton
    class="relative inline-flex w-72 rounded-md border border-gray-400 bg-white py-3 pl-6  text-xl font-semibold text-gray-800 shadow-sm shadow-blue-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-gray-100"
  >
    {namemap[cmd.op]}
    <svg xmlns="http://www.w3.org/2000/svg" class="absolute right-0 ml-2 mr-2 h-5 w-5 self-center" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 9l4-4 4 4m0 6l-4 4-4-4" />
    </svg>
  </MenuButton>
  <MenuItems class="absolute left-0 z-40 mt-2 w-64 rounded-md border border-gray-200 bg-white shadow-xl focus:outline-none">
    <div class="dropp divide-y divide-gray-200" transition:fade={{ duration: 100, easing: cubicInOut }}>
      <section>
        <MenuItem let:active><div on:click={handleClick("hold")} class:bg-blue-200={active} class="item">{namemap["hold"]}</div></MenuItem>
        <MenuItem let:active><div on:click={handleClick("goto")} class:bg-blue-200={active} class="item">{namemap["goto"]}</div></MenuItem>
      </section>

      <section>
        <MenuItem let:active><div on:click={handleClick("pump")} class:bg-gray-200={active} class="item">{namemap["pump"]}</div></MenuItem>
        <MenuItem let:active><div on:click={handleClick("prime")} class:bg-gray-200={active} class="item">{namemap["prime"]}</div></MenuItem>
        <MenuItem let:active><div on:click={handleClick("temp")} class:bg-gray-200={active} class="item">{namemap["temp"]}</div></MenuItem>
      </section>
      <section>
        <MenuItem let:active><div on:click={handleClick("autofocus")} class:bg-gray-200={active} class="item">{namemap["autofocus"]}</div></MenuItem>
        <MenuItem let:active><div on:click={handleClick("takeimage")} class:bg-gray-200={active} class="item">{namemap["takeimage"]}</div></MenuItem>
      </section>
    </div>
  </MenuItems>
</Menu>

<style lang="postcss">
  section {
    @apply py-1;
  }
  .item {
    @apply block w-full bg-white px-4 py-2 text-left font-medium hover:bg-blue-100 hover:text-blue-800;
  }

  .dropp::before {
    @apply absolute inline-block;
    content: "";
    border: 8px solid transparent;
    border-bottom-color: #e5e7eb;

    top: -15px;
    right: 11px;
    left: auto;
  }

  .dropp::after {
    @apply absolute inline-block;
    border: 7px solid transparent;
    content: "";
    border-bottom-color: white;
    top: -12px;
    right: 12px;
    left: auto;
  }
</style>
