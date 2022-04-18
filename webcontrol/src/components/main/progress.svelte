<script lang="ts">
  import { cubicOut } from "svelte/easing";
  import { tweened } from "svelte/motion";

  export const progress = tweened(0, {
    duration: 400,
    easing: cubicOut,
  });
</script>

<span class="z-40 flex w-full space-x-2">
  <slot name="buttons" />

  <!-- Big box -->
  <content class="flex-grow rounded-lg border border-base-300 bg-white/60 px-4 py-2">
    <slot />

    <!-- Lower bar -->

    <div class="mt-1">
      <progress class="relative h-2 w-full appearance-none overflow-hidden rounded-lg shadow" value={$progress} />
    </div>
  </content>
</span>

<style lang="postcss">
  progress {
    @apply bg-gray-50;
  }

  progress::-moz-progress-bar {
    @apply bg-gray-200;
  }

  progress::-webkit-progress-bar {
    @apply bg-gray-200;
  }

  progress::-webkit-progress-value {
    @apply rounded bg-gradient-to-r from-indigo-600 to-blue-500;
  }
</style>
