<script lang="ts">
  export let name: string = "";
  export let path: string = "";
</script>

<div class="grid grid-cols-4 font-medium mt-2 text-lg">
  <div>
    Name <input type="text" class="pretty" bind:value={name} />
  </div>
  <div>
    Path <input type="text" class="pretty" bind:value={path} />
  </div>
</div>
