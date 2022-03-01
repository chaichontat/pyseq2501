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
  <content class="flex-grow px-4 py-2 border rounded-lg border-base-300">
    <slot />

    <!-- Lower bar -->

    <div class="mt-1">
      <progress class="relative w-full h-2 overflow-hidden rounded-lg shadow appearance-none" value={$progress} />
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
    @apply bg-gradient-to-r from-indigo-600 to-blue-500 rounded;
  }
</style>
