<script lang="ts">
  import Logo from "$comps/logo.svelte";
  import Connected from "$comps/navbar/connected.svelte";
  import Status from "$comps/navbar/status.svelte";
  import { userStore as us } from "$src/store";

  // Mode controlled here.
</script>

<div id="nav" class="sticky inset-x-0 top-0 z-50 w-full h-16 transition duration-200 ease-in-out bg-white shadow-sm opacity-95 text-base-content ring-1 ring-gray-900 ring-opacity-5">
  <div class="mx-auto space-x-1 navbar max-w-none">
    <div class="flex-none">
      <label for="main-menu" class="btn btn-square btn-ghost drawer-button lg:hidden">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="inline-block w-6 h-6 stroke-current">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
        </svg>
      </label>
    </div>

    <div class="flex items-center flex-none lg:hidden">
      <Logo />
    </div>

    <Status />

    <div class="flex-1" />

    <Connected />
    <!-- 
    <div class="border-b border-gray-200 dark:border-gray-700">
      <ul class="flex flex-wrap -mb-0.5 transition-all">
        <li class="mr-2">
          <a
            href="#"
            class="inline-flex px-4 py-4 text-lg font-medium text-center text-gray-500 border-b-2 border-transparent rounded-t-lg hover:text-gray-600 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300 group"
          >
            <svg
              class="w-5 h-5 mr-2 text-gray-400 group-hover:text-gray-500 dark:text-gray-500 dark:group-hover:text-gray-300"
              fill="currentColor"
              viewBox="0 0 20 20"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                fill-rule="evenodd"
                d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-6-3a2 2 0 11-4 0 2 2 0 014 0zm-2 4a5 5 0 00-4.546 2.916A5.986 5.986 0 0010 16a5.986 5.986 0 004.546-2.084A5 5 0 0010 11z"
                clip-rule="evenodd"
              />
            </svg>
            Manual
          </a>
        </li>
        <li class="mr-2">
          <a
            href="#"
            class="inline-flex px-4 py-4 text-lg font-medium text-center text-blue-600 border-b-2 border-blue-600 rounded-t-lg active dark:text-blue-500 dark:border-blue-500 group"
            aria-current="page"
          >
            <svg class="w-5 h-5 mr-2 text-blue-600 dark:text-blue-500" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
              <path
                d="M5 3a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2V5a2 2 0 00-2-2H5zM5 11a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2v-2a2 2 0 00-2-2H5zM11 5a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V5zM11 13a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"
              />
            </svg>
            Automatic
          </a>
        </li>
      </ul>
    </div> -->

    <div class="tabs">
      <button
        class="font-medium transition-colors h-14 tab tab-lg tab-bordered"
        on:click={() => ($us.mode = "manual")}
        class:tab-active={$us.mode === "manual"}
        class:text-gray-800={$us.mode === "manual"}
      >
        Manual
      </button>
      <button
        class="font-medium transition-colors h-14 tab tab-lg tab-bordered"
        on:click={() => ($us.mode = "automatic")}
        class:tab-active={$us.mode !== "manual"}
        class:text-gray-800={$us.mode !== "manual"}
      >
        Automatic
      </button>
    </div>

    <div title="Github ↗︎" class="items-center flex-none pr-4">
      <a target="_blank" href="https://github.com/chaichontat/pyseq2501-web" rel="noopener" class="normal-case btn btn-ghost drawer-button btn-square">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" class="inline-block w-6 h-6 fill-current">
          <path
            d="M256,32C132.3,32,32,134.9,32,261.7c0,101.5,64.2,187.5,153.2,217.9a17.56,17.56,0,0,0,3.8.4c8.3,0,11.5-6.1,11.5-11.4,0-5.5-.2-19.9-.3-39.1a102.4,102.4,0,0,1-22.6,2.7c-43.1,0-52.9-33.5-52.9-33.5-10.2-26.5-24.9-33.6-24.9-33.6-19.5-13.7-.1-14.1,1.4-14.1h.1c22.5,2,34.3,23.8,34.3,23.8,11.2,19.6,26.2,25.1,39.6,25.1a63,63,0,0,0,25.6-6c2-14.8,7.8-24.9,14.2-30.7-49.7-5.8-102-25.5-102-113.5,0-25.1,8.7-45.6,23-61.6-2.3-5.8-10-29.2,2.2-60.8a18.64,18.64,0,0,1,5-.5c8.1,0,26.4,3.1,56.6,24.1a208.21,208.21,0,0,1,112.2,0c30.2-21,48.5-24.1,56.6-24.1a18.64,18.64,0,0,1,5,.5c12.2,31.6,4.5,55,2.2,60.8,14.3,16.1,23,36.6,23,61.6,0,88.2-52.4,107.6-102.3,113.3,8,7.1,15.2,21.1,15.2,42.5,0,30.7-.3,55.5-.3,63,0,5.4,3.1,11.5,11.4,11.5a19.35,19.35,0,0,0,4-.4C415.9,449.2,480,363.1,480,261.7,480,134.9,379.7,32,256,32Z"
          />
        </svg>
      </a>
    </div>
  </div>
</div>
