<script lang="ts">
  import { createEventDispatcher } from "svelte";

  export let editable: boolean = false;
  export let value: number = 0;
  export let clInp: string = "text-center self-center";
  export let clDisp: string = "text-center self-center";
  let elem: HTMLInputElement;

  const dispatch = createEventDispatcher();
  const focus = (el: HTMLElement) => el.focus();
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
    if (!validator(value)) {
      focus(elem);
      return;
    }
    editable = false;
    dispatch("set", value);
  }
</script>

{#if editable}
  <input
    type="number"
    class={clInp}
    bind:value
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

  input::-webkit-outer-spin-button,
  input::-webkit-inner-spin-button {
    -webkit-appearance: none;
    margin: 0;
  }
  input[type="number"] {
    -moz-appearance: textfield;
  }
</style>
