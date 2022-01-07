<script lang="ts">
  import { createEventDispatcher } from "svelte";

  export let editable: boolean = false;
  export let value: number | string = 0;
  export let userValue: number = 0;
  export let clInp: string = "text-center self-center";
  export let clDisp: string = "text-center self-center";
  let elem: HTMLInputElement;

  const dispatch = createEventDispatcher();
  const focus = (el: HTMLInputElement) => {
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
    editable = false;
    dispatch("set", userValue);
  }
</script>

{#if editable}
  <input
    type="number"
    class={clInp}
    bind:value={userValue}
    on:keypress={handleInput}
    on:blur={focuslost}
    bind:this={elem}
    use:focus
  />
{:else}
  <div class={clDisp} on:dblclick={() => (editable = true)}>
    {value}
  </div>
{/if}

<style lang="postcss">
  .input-smaller {
    @apply text-sm font-medium leading-none h-6 px-2;
  }

  .input-normal {
    @apply text-lg font-medium leading-none h-6 px-2;
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
