<script lang="ts">
  export let name: string;
  export let value: number | string;
</script>

<div class="flex self-center">
  <div class="flex flex-col">
    <span class="w-24 font-medium text-center">{name}</span>
    <span class="font-mono font-medium leading-6 text-center">{value}</span>
  </div>
</div>
