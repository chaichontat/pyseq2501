<script lang="ts">
  export let name: string = "";
  export let path: string = "";
</script>

<div class="flex flex-col mt-2 space-y-2 text-lg font-medium">
  <div>
    Name <input type="text" class="pretty" bind:value={name} />
  </div>
  <div>
    Image Path <input type="text" class="pretty" bind:value={path} />
  </div>
</div>
