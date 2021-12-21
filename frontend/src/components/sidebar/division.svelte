<script lang="ts">
  export let name;
</script>

<li class="mt-4 menu-title ">
  <span style="--tw-text-opacity: 0.6; padding-left:1rem; font-size:1em;">{name}</span>
</li>
<div class="elem">
  <slot />
</div>

<style lang="postcss">
  .elem {
    font-size: 0.875rem;
    line-height: 1.25rem;
    padding: 0.75rem 1rem;
  }
</style>
