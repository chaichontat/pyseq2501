<script lang="ts">
  export let name_: string;
  export let value: number | string;
</script>

<div class="flex self-center">
  <div class="flex flex-col">
    <span class="w-24 text-center font-medium">{name_}</span>
    <span class="text-center font-mono font-medium leading-6">{value}</span>
  </div>
</div>
