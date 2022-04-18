<script lang="ts">
  import { createEventDispatcher } from "svelte";
  import { localStore as ls } from "$src/stores/store";
  let cl = "";
  export { cl as class };

  const dispatch = createEventDispatcher();

  function click() {
    if ($ls.mode === "manual") {
      dispatch("click", true);
    }
  }
</script>

<button class={cl} on:click={click} class:cursor-default={$ls.mode !== "manual"}>
  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 fill-gray-700 transition-colors" class:fill-gray-300={$ls.mode !== "manual"} viewBox="0 0 20 20">
    <path d="M17.414 2.586a2 2 0 00-2.828 0L7 10.172V13h2.828l7.586-7.586a2 2 0 000-2.828z" />
    <path fill-rule="evenodd" d="M2 6a2 2 0 012-2h4a1 1 0 010 2H4v10h10v-4a1 1 0 112 0v4a2 2 0 01-2 2H4a2 2 0 01-2-2V6z" clip-rule="evenodd" />
  </svg>
</button>
