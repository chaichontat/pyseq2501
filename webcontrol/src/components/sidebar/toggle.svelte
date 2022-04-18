<script lang="ts">
  import { joinClass } from "$src/utils";
  import { Switch } from "@rgossiaux/svelte-headlessui";

  export let checked: boolean;
  export let disabled = false;

  function genColor(che: boolean, dis: boolean): string {
    if (dis) return "bg-gray-500 opacity-40 cursor-default";
    if (che) return "bg-purple-600";
    return "bg-indigo-600";
  }

  let cl = "";
  $: cl = joinClass(
    genColor(checked, disabled),
    "relative inline-flex h-[24px] w-[48px] flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-all duration-200 ease-in-out focus:outline-none focus-visible:ring-2  focus-visible:ring-white focus-visible:ring-opacity-75"
  );
</script>

<Switch on:change={() => (checked = !checked)} class={cl} {disabled}>
  <span
    aria-hidden="true"
    class={`${checked ? "translate-x-6" : "translate-x-0"} thing pointer-events-none inline-block h-[20px] w-[20px] transform bg-white shadow ring-0 transition duration-200 ease-in-out`}
    style="border-radius: 50%;"
  />
</Switch>
