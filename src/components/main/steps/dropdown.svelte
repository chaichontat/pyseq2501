<script lang="ts">
  export let curr = "Wash";
  let showing: boolean = false;
</script>

<!-- This example requires Tailwind CSS v2.0+ -->
<div class="relative inline-block text-left">
  <div>
    <button
      type="button"
      class="relative text-lg pl-6 inline-flex w-64 rounded-md border border-gray-300 shadow-sm py-2 bg-white font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-100 focus:ring-indigo-500"
      aria-expanded="true"
      aria-haspopup="true"
      on:blur={() => (showing = false)}
      on:click={() => (showing = !showing)}
    >
      <b>{curr}</b>

      <!-- Heroicon name: solid/chevron-down -->
      <svg
        class="absolute mr-2 ml-2 h-5 w-5 right-0 self-center"
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 20 20"
        fill="currentColor"
        aria-hidden="true"
      >
        <path
          fill-rule="evenodd"
          d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z"
          clip-rule="evenodd"
        />
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
    class:scale-100={!showing}
    class="list transition ease-in scale-95 duration-75 z-10 absolute left-0 mt-2 w-64 rounded-md shadow-xl bg-white ring-1 ring-black ring-opacity-5 divide-y divide-gray-200 focus:outline-none"
    role="menu"
    tabindex="-1"
  >
    <section>
      <!-- Active: "bg-gray-100 text-gray-900", Not Active: "text-gray-700" -->
      <div href="#" on:click={() => (curr = "Hold")}>Hold</div>
    </section>
    <section>
      <!-- Active: "bg-gray-100 text-gray-900", Not Active: "text-gray-700" -->
      <div on:click={() => (curr = "Wash")}>Wash</div>
      <div on:click={() => (curr = "Prime")}>Prime</div>
      <div on:click={() => (curr = "Change Temperature")}>Change Temperature</div>
    </section>
    <section>
      <div on:click={() => (curr = "Image")}>Image</div>
      <div on:click={() => (curr = "Move Stage")}>Move Stage</div>
    </section>
  </div>
</div>

<style lang="postcss">
  .list > section {
    @apply py-1;
  }
  .list > * > * {
    @apply text-gray-900 block px-4 py-2 font-medium cursor-pointer;
  }
  .list > * > :hover {
    @apply bg-gray-100 text-black;
  }
</style>
