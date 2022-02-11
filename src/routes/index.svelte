<script lang="ts">
  import Preview from "$comps/main/preview.svelte";
  import { userStore as us } from "$src/store";
  import ProgressManual from "$src/components/main/manual/progress_manual.svelte";
  import { fade } from "svelte/transition";
  import MainAuto from "./main_auto.svelte";

  const duration: number = 150;
</script>

{#if $us.mode !== "manual"}
  <div out:fade={{ duration }} in:fade={{ duration, delay: duration }}>
    <MainAuto />
  </div>
{:else}
  <div out:fade={{ duration }} in:fade={{ duration, delay: duration }}>
    <ProgressManual />
    <p class="mt-6 mb-1 text-2xl font-bold text-gray-600">Preview</p>
    <Preview />
  </div>
{/if}

<!-- End line -->
<div class="flex h-36">
  <div class="self-center w-2/5 mx-auto border-t border-gray-200" />
</div>

<button
  id="dropdownButton"
  data-dropdown-toggle="dropdown"
  class="text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:ring-blue-300 font-medium rounded-lg text-sm px-4 py-2.5 text-center inline-flex items-center dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800"
  type="button"
>
  Dropdown button <svg class="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
  </svg>
</button>

<div id="dropdown" class="z-10 hidden text-base list-none bg-white divide-y divide-gray-100 rounded shadow w-44 dark:bg-gray-700">
  <ul class="py-1" aria-labelledby="dropdownButton">
    <li>
      <a href="#" class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600 dark:text-gray-200 dark:hover:text-white">Dashboard</a>
    </li>
    <li>
      <a href="#" class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600 dark:text-gray-200 dark:hover:text-white">Settings</a>
    </li>
    <li>
      <a href="#" class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600 dark:text-gray-200 dark:hover:text-white">Earnings</a>
    </li>
    <li>
      <a href="#" class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600 dark:text-gray-200 dark:hover:text-white">Sign out</a>
    </li>
  </ul>
</div>
