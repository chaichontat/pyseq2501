<script lang="ts">
  export let name: string;
</script>

<li class="mb-6">
  <span class="font-bold opacity-60">{name}</span>
  <div class="pl-4 pr-2">
    <slot />
  </div>
</li>
