<script lang="ts">
  import type { Ops } from "$src/cmds";

  export let cmd: Ops = "pump";
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
      cmd = target;
      showing = false;
    };
  }
</script>

<!-- This example requires Tailwind CSS v2.0+ -->
<div class="relative inline-block text-left">
  <div>
    <button
      type="button"
      class="relative text-lg pl-6 inline-flex w-64 rounded-md border border-gray-300 shadow-sm py-2 bg-white font-medium text-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-100 focus:ring-indigo-500"
      aria-expanded="true"
      aria-haspopup="true"
      on:click={() => (showing = !showing)}
      on:blur={() => (showing = false)}
    >
      <b>{namemap[cmd]}</b>

      <!-- Heroicon name: solid/chevron-down -->
      <svg class="absolute mr-2 ml-2 h-5 w-5 right-0 self-center" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
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
    class="list transition ease-in scale-95 duration-75 z-10 absolute left-0 mt-2 w-64 rounded-md shadow-xl bg-white ring-1 ring-black ring-opacity-5 divide-y divide-gray-200 focus:outline-none"
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
