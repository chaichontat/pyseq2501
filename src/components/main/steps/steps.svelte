<script>
  import Cell from "./cell.svelte";
</script>

<div class="my-8">
  <p class="text-gray-600 font-bold text-2xl pb-3 border-b">Steps</p>
  <ul class="divide-y divide-gray-500">
    <Cell n={1} />
    <Cell n={2} />
    <Cell n={3} />
  </ul>

  <button
    type="button"
    class="transition-colors shadow-lg shadow-blue-500/50 text-white bg-blue-600 hover:bg-blue-700 focus:ring-4 focus:ring-blue-300 font-medium rounded-lg px-5 py-2.5 text-center inline-flex items-center mr-2 dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800"
  >
    <svg
      class="-ml-2 mr-1 w-6 h-6"
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      xmlns="http://www.w3.org/2000/svg"
      ><path
        stroke-linecap="round"
        stroke-linejoin="round"
        stroke-width="2"
        d="M12 6v6m0 0v6m0-6h6m-6 0H6"
      /></svg
    >
    Add Step
  </button>
</div>
