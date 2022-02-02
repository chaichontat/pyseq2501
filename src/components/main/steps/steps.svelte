<script>
  import Cell from "./step_cell.svelte";
  import Reagents from "./reagents.svelte";
</script>

<div class="my-8 w-full">
  <p class="text-gray-600 font-bold text-2xl pb-3 border-b">Details</p>
  <div class="grid grid-cols-4 font-medium mt-2 text-lg">
    <div>
      Name <input type="text" class="pretty" />
    </div>
    <div>
      Path <input type="text" class="pretty" />
    </div>
  </div>

  <Reagents />

  <p class="text-gray-600 font-bold text-2xl py-3 border-b mt-6">Steps</p>
  <ul>
    <Cell n={1} />
    <Cell n={2} />
    <Cell n={3} />

    <li
      id="add"
      class="text-lg transition-all border-y border-gray-400 hover:border-blue-500 inline-flex items-center justify-center cursor-pointer w-full h-16 font-medium hover:font-semibold white-clickable hover:bg-gray-50"
    >
      <span class="inline-flex">
        <svg id="inner" stroke-width="1.5" class="-ml-2 mr-1 w-6 h-6 transition-all my-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" xmlns="http://www.w3.org/2000/svg">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
        </svg>
        Add Step
      </span>
    </li>
  </ul>
</div>

<style lang="postcss">
  #add:hover #inner {
    stroke-width: 2;
  }
</style>
