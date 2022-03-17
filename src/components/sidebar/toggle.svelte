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
    relative inline-flex h-[24px] w-[48px] flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-all duration-200 ease-in-out focus:outline-none focus-visible:ring-2  focus-visible:ring-white focus-visible:ring-opacity-75`}
  disabled={$ls.mode.startsWith("editing")}
>
  <span
    aria-hidden="true"
    class={`${checked ? "translate-x-6" : "translate-x-0"} thing pointer-events-none inline-block h-[20px] w-[20px] transform bg-white shadow ring-0 transition duration-200 ease-in-out`}
    style="border-radius: 50%;"
  />
</Switch>
