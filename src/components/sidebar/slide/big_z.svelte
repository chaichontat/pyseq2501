<script lang="ts">
  import Pencil from "../../svgs/pencil.svelte";
  import Editable from "./editable.svelte";

  export let name = "";
  export let value: number | string = -1;
  export let userValue: number = -1;

  let editing: boolean = false;
</script>

<div class="flex self-center">
  <div class="flex flex-col">
    <span class="w-24 font-medium text-center">{name}</span>
    <Editable bind:editing bind:userValue {value} clDisp="leading-6 font-mono font-medium text-center" clInp="w-24 text-base input input-smaller text-center" />
  </div>
  <Pencil class="ml-2" on:click={() => (editing = true)} />
</div>
