<script lang="ts">
  export let name: "A" | "B";
  import { userStore as us } from "$src/store";

  function handleEditClick(): () => void {
    return () => {
      $us.mode = `editing${name}`;
      $us.flowcell = name === "B";
    };
  }
</script>

<div class="w-4/12 max-w-md p-6 space-y-2 bg-white border border-gray-200 rounded-lg shadow-md dark:bg-gray-800 dark:border-gray-700">
  <div class="flex">
    <p class="mb-4 text-6xl font-bold text-gray-600">{name}</p>
    <!-- Spacer -->
    <div class="grow" />
    <button type="button" class="px-4 py-2 font-medium rounded-lg max-h-10 white-button" on:click={handleEditClick()}>
      <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
      </svg>
      Edit
    </button>
  </div>

  <span class="text-base font-medium text-blue-700 dark:text-white">Steps 3/7: Washing with water</span>

  <div class="flex justify-between mb-1">
    <span class="text-base font-medium text-blue-700 dark:text-white">Time remaining</span>
    <span class="text-sm font-medium text-blue-700 dark:text-white">14 min</span>
  </div>

  <div class="w-full bg-gray-200 rounded-full h-2.5 dark:bg-gray-700">
    <div class="bg-blue-600 h-2.5 rounded-full" style="width: 45%" />
  </div>
</div>
