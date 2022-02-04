<script lang="ts">
  export let name: string = "";
  export let path: string = "";
</script>

<div class="mt-2 text-lg font-medium grid grid-cols-4">
  <div>
    Name <input type="text" class="pretty" bind:value={name} />
  </div>
  <div>
    Path <input type="text" class="pretty" bind:value={path} />
  </div>
</div>
