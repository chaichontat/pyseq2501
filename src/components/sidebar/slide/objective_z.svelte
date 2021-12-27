<script lang="ts">
  import Pencil from "../../svgs/pencil.svelte";
  import Editable from "./editable.svelte";

  let editable: boolean = false;
  let value: number = 0;
</script>

<div class="ml-6 mt-3 flex self-center text-sm">
  <div class="flex flex-col">
    Objective Z:&nbsp;
    <Editable
      bind:editable
      {value}
      clDisp="leading-6 font-mono font-medium text-center"
      clInp="w-20 text-sm text-base input input-smaller text-center"
    />
  </div>
  <Pencil class="ml-2" on:click={() => (editable = true)} />
</div>
