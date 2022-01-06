<script lang="ts">
  import Pencil from "../../svgs/pencil.svelte";
  import Editable from "./editable.svelte";

  export let name = "";

  let editable: boolean = false;
  let value: number = 0;
</script>

<div class="flex self-center">
  <div class="flex flex-col">
    <span class="w-24 text-center font-medium">{name}</span>
    <Editable
      bind:editable
      {value}
      clDisp="leading-6 font-mono font-medium text-center"
      clInp="w-24 text-base input input-normal text-center"
    />
  </div>
  <Pencil class="ml-2" on:click={() => (editable = true)} />
</div>
