<script lang="ts">
  import type { Cmd, Ops } from "$src/cmds";
  import { defaults } from "$src/cmds";

  export let cmd: Cmd = { ...defaults.pump };
  let showing: boolean = false;

  const namemap = {
    pump: "Pump",
    prime: "Prime",
    temp: "Change Temperature",
    hold: "Hold",
    move: "Move",
    image: "Image",
  };

  function handleClick(target: Ops) {
    return () => {
      cmd = { ...defaults[target] };
      showing = false;
    };
  }
</script>

<!-- This example requires Tailwind CSS v2.0+ -->
<div class="relative inline-block text-left">
  <div>
    <button
      type="button"
      class="relative inline-flex w-64 py-2 pl-6 text-lg font-medium text-gray-700 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-100 focus:ring-indigo-500"
      aria-expanded="true"
      aria-haspopup="true"
      on:click={() => (showing = !showing)}
      on:blur={() => (showing = false)}
    >
      <b>{namemap[cmd.op]}</b>

      <!-- Heroicon name: solid/chevron-down -->
      <svg class="absolute right-0 self-center w-5 h-5 ml-2 mr-2" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
        <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
      </svg>
    </button>
  </div>

  <!--
      Dropdown menu, show/hide based on menu state.
  
      Entering: "transition ease-out duration-100"
        From: "transform opacity-0 scale-95"
        To: "transform opacity-100 scale-100"
      Leaving: "transition ease-in duration-75"
        From: "transform opacity-100 scale-100"
        To: "transform opacity-0 scale-95"
    -->
  <div
    class:opacity-0={!showing}
    class:invisible={!showing}
    class:scale-100={!showing}
    class="absolute left-0 z-10 w-64 mt-2 bg-white shadow-xl transition duration-75 ease-in scale-95 divide-y divide-gray-200 rounded-md list ring-1 ring-black ring-opacity-5 focus:outline-none"
    role="menu"
    id="list"
    tabindex="-1"
    on:blur={() => (showing = false)}
  >
    <section>
      <!-- Active: "bg-gray-100 text-gray-900", Not Active: "text-gray-700" -->
      <div on:mousedown={handleClick("hold")}>{namemap["hold"]}</div>
      <!-- Mousedown fires before blur -->
    </section>
    <section>
      <div on:mousedown={handleClick("pump")}>{namemap["pump"]}</div>
      <div on:mousedown={handleClick("prime")}>{namemap["prime"]}</div>
      <div on:mousedown={handleClick("temp")}>{namemap["temp"]}</div>
    </section>
    <section>
      <div on:mousedown={handleClick("image")}>{namemap["image"]}</div>
      <div on:mousedown={handleClick("move")}>{namemap["move"]}</div>
    </section>
  </div>
</div>

<style lang="postcss">
  .list > section {
    @apply py-1;
  }
  .list > * > * {
    @apply text-gray-900 block px-4 py-2 font-medium cursor-pointer bg-white;
  }
  .list > * > :hover {
    @apply bg-gray-100 text-black;
  }
</style>
