<script lang="ts">
  import { Dialog, DialogOverlay, DialogTitle } from "@rgossiaux/svelte-headlessui";
  import { cubicInOut } from "svelte/easing";
  import { fade } from "svelte/transition";
  export let title = "";
  let opened = false;
  let clickClose = true;
</script>

<div class="flex items-center justify-center">
  <div on:click={() => (opened = true)}>
    <slot name="button">
      <button
        type="button"
        class="rounded-md bg-black bg-opacity-20 px-4 py-2 text-sm font-medium text-white hover:bg-opacity-30 focus:outline-none focus-visible:ring-2 focus-visible:ring-white focus-visible:ring-opacity-75"
      >
        Open dialog
      </button>
    </slot>
  </div>
</div>

<Dialog class="fixed inset-0 z-10 overflow-y-auto" bind:open={opened} on:cl={() => (opened = false)}>
  <div class="min-h-screen px-4 text-center">
    <div transition:fade={{ duration: 100, easing: cubicInOut }}>
      <DialogOverlay
        class="fixed inset-0 cursor-pointer bg-black opacity-40 transition-all"
        on:click={() => {
          if (clickClose) opened = false;
        }}
      />
    </div>

    <!-- {/* This element is to trick the browser into centering the modal contents. */} -->
    <span class="inline-block h-screen align-middle" aria-hidden="true">&#8203;</span>

    <div transition:fade={{ duration: 100, easing: cubicInOut }} class="my-8 inline-block max-w-7xl transform overflow-hidden rounded-2xl bg-white p-6 text-left align-middle shadow-xl transition-all">
      <DialogTitle class="text-lg font-medium leading-6 text-gray-900">{title}</DialogTitle>
      <slot />
    </div>
  </div>
</Dialog>
