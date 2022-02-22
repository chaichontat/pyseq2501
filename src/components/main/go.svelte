<script lang="ts">
  import Spinning from "../spinning.svelte";

  export let disabled: boolean = false;
  export let spin: boolean = false;
</script>

<button
  type="button"
  class="px-4 py-1 text-sm font-medium text-blue-800 border-blue-300 rounded-lg w-14 hover:bg-blue-100 active:bg-blue-200 bg-blue-50 white-button disabled:bg-gray-50 disabled:hover:bg-gray-50 disabled:active:bg-gray-50 disabled:text-gray-500"
  tabindex="0"
  {disabled}
>
  {#if spin}
    <div class="mx-auto opacity-40">
      <Spinning color="black" />
    </div>
  {:else}
    <div class="mx-auto"><slot>Go</slot></div>
  {/if}
</button>
