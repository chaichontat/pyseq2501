<script lang="ts">
  import { createEventDispatcher } from "svelte";

  export let editing = false;
  export let value: number | string = 0;
  export let userValue = 0;
  export let clInp = "text-center self-center";
  export let clDisp = "text-center self-center";

  const dispatch = createEventDispatcher();
  const setFocus = (el: HTMLInputElement) => {
    el.focus();
    el.select();
  };
  function validator(x: number) {
    return 0 <= x && x <= 65535;
  }

  function handleInput(event: KeyboardEvent) {
    if (event.key != "Enter") {
      return;
    }
    focuslost();
  }

  function focuslost() {
    editing = false;
    dispatch("set", userValue);
  }
</script>

{#if editing}
  <input type="number" class={clInp} bind:value={userValue} on:keypress={handleInput} on:blur={focuslost} use:setFocus />
{:else}
  <div class={clDisp} on:dblclick={() => (editing = true)}>
    {value}
  </div>
{/if}

<style lang="postcss">
  .input-smaller {
    @apply h-6 px-2 text-sm font-medium leading-none;
  }

  .input-normal {
    @apply h-6 px-2 text-lg font-medium leading-none;
    /* font-size: 1.06125rem; */
  }

  input::-webkit-outer-spin-button,
  input::-webkit-inner-spin-button {
    -webkit-appearance: none;
    margin: 0;
  }
  input[type="number"] {
    -moz-appearance: textfield;
  }

  input:invalid {
    @apply border-red-600;
    text-decoration: line-through;
  }

  input:valid {
    @apply border-gray-400;
    text-decoration: none;
  }
</style>
