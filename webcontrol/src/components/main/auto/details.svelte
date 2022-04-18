<script lang="ts">
  export let name_ = "";
  export let path = "";
</script>

<div class="flex flex-col text-lg font-medium">
  <p class="text-lg">Name</p>
  <input type="text" class="pretty mt-1 mb-4 max-w-md" bind:value={name_} class:invalid={!name_} />

  <p class="text-lg">Image Path</p>
  <input type="text" class="pretty mt-1 mb-4 max-w-md" bind:value={path} class:invalid={!path} />
</div>
