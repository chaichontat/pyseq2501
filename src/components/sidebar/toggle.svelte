<script lang="ts">
  import { Switch, SwitchLabel } from "@rgossiaux/svelte-headlessui";

  export let checked = false;
</script>

<Switch
  on:change={() => (checked = !checked)}
  class={`${checked ? "bg-indigo-600" : "bg-blue-700"}
    relative inline-flex flex-shrink-0 h-[24px] w-[48px] border-2 border-transparent rounded-full cursor-pointer transition-colors ease-in-out duration-200 focus:outline-none focus-visible:ring-2  focus-visible:ring-white focus-visible:ring-opacity-75`}
>
  <span
    aria-hidden="true"
    class={`${checked ? "translate-x-6" : "translate-x-0"} thing pointer-events-none inline-block h-[20px] w-[20px] bg-white shadow transform ring-0 transition ease-in-out duration-200`}
    style="border-radius: 50%;"
  />
</Switch>
