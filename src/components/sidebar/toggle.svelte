<script lang="ts">
  import { localStore as ls } from "$src/stores/store";
  import { Switch } from "@rgossiaux/svelte-headlessui";
  export let checked = false;

  const m = $ls.mode;
  function genColor(x: typeof m) {
    switch (x) {
      case "editingA":
        return "bg-indigo-600";
      case "editingB":
        return "bg-purple-600";
      default:
        return "bg-blue-700";
    }
  }

  $: switch ($ls.mode) {
    case "editingA":
      checked = false;
      break;
    case "editingB":
      checked = true;
      break;
  }
</script>

<Switch
  on:change={() => (checked = !checked)}
  class={`${genColor($ls.mode)} ${$ls.mode.startsWith("editing") ? "opacity-40" : ""}
    relative inline-flex flex-shrink-0 h-[24px] w-[48px] border-2 border-transparent rounded-full cursor-pointer transition-all ease-in-out duration-200 focus:outline-none focus-visible:ring-2  focus-visible:ring-white focus-visible:ring-opacity-75`}
  disabled={$ls.mode.startsWith("editing")}
>
  <span
    aria-hidden="true"
    class={`${checked ? "translate-x-6" : "translate-x-0"} thing pointer-events-none inline-block h-[20px] w-[20px] bg-white shadow transform ring-0 transition ease-in-out duration-200`}
    style="border-radius: 50%;"
  />
</Switch>
