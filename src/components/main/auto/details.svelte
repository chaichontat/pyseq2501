<script lang="ts">
  export let name: string = "";
  export let path: string = "";
</script>

<div class="flex flex-col mt-2 text-lg font-medium">
  <p class="text-lg">Name</p>
  <input type="text" class="max-w-md mt-1 mb-4 pretty" bind:value={name} class:invalid={!name} />

  <p class="text-lg">Image Path</p>
  <input type="text" class="max-w-md mt-1 mb-4 pretty" bind:value={path} class:invalid={!path} />
</div>
