<script lang="ts">
  export let fc: boolean;
  import { userStore as us, localStore as ls } from "$src/stores/store";

  function handleEditClick(): () => void {
    return () => {
      $ls.mode = fc ? "editingB" : "editingA";
      $us.image_params.fc = fc;
    };
  }
</script>

<div class="w-4/12 max-w-md space-y-3 rounded-lg border bg-white p-6 text-lg shadow shadow-indigo-300" class:shadow-purple-300={fc}>
  <div class="flex">
    <p class="mb-4 text-6xl font-bold text-gray-700">{fc ? "B" : "A"}</p>
    <!-- Spacer -->
    <div class="grow" />
    <button type="button" class="white-button max-h-10 rounded-lg px-4 py-2 font-medium" on:click={handleEditClick()}>
      <svg xmlns="http://www.w3.org/2000/svg" class="mr-1 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
      </svg>
      Edit
    </button>
  </div>

  <span class="text-2xl font-semibold text-green-700 dark:text-white">Ready</span>

  <div class="my-1 flex justify-between">
    <span class="font-medium text-indigo-800 dark:text-white" class:text-purple-800={fc}>Time remaining</span>
    <span class="text-lg font-semibold text-indigo-800 dark:text-white" class:text-purple-800={fc}>14 min</span>
  </div>

  <div class="h-2.5 w-full rounded-full bg-gray-200 dark:bg-gray-800">
    <div class="h-2.5 rounded-full bg-indigo-700" class:bg-purple-800={fc} style="width: 45%" />
  </div>
</div>
