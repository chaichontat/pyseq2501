<script lang="ts">
  import { createEventDispatcher } from "svelte";
  import Spinning from "../spinning.svelte";
  export let disabled = false;
  export let spin = false;
  export let color: "blue" | "indigo" | "green" | "sky" = "indigo";
  export let cl = "";

  const dispatch = createEventDispatcher();

  const colorMap: { [key in typeof color]: string } = {
    blue: "text-blue-800 border-blue-300 hover:bg-blue-100 active:bg-blue-200 bg-blue-50",
    indigo: "text-indigo-800 border-indigo-300 hover:bg-indigo-100 active:bg-indigo-200 bg-indigo-50",
    green: "text-green-800 border-green-300 hover:bg-green-100 active:bg-green-200 bg-green-50",
    sky: "text-sky-800 border-sky-300 hover:bg-sky-100 active:bg-sky-200 bg-sky-50",
  };
</script>

<button
  type="button"
  class={`white-button rounded-lg px-4 py-1 text-sm font-semibold transition-all duration-100 ${colorMap[color]} disabled:bg-gray-50 disabled:text-gray-500 disabled:hover:bg-gray-50 disabled:active:bg-gray-50 ${cl}`}
  tabindex="0"
  on:click={() => dispatch("click")}
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

<style lang="postcss">
  .blue {
    @apply border-blue-300 bg-blue-50 text-blue-800 hover:bg-blue-100 active:bg-blue-200;
  }
</style>
