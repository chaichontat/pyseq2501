<script lang="ts">
  import { Dialog, DialogOverlay, DialogTitle } from "@rgossiaux/svelte-headlessui";
  import { cubicInOut } from "svelte/easing";
  import { fade } from "svelte/transition";
  export let title = "";
  let open: boolean = false;
  let clickClose: boolean = true;
</script>

<div class="flex items-center justify-center">
  <div on:click={() => (open = true)}>
    <slot name="button">
      <button
        type="button"
        class="px-4 py-2 text-sm font-medium text-white bg-black rounded-md bg-opacity-20 hover:bg-opacity-30 focus:outline-none focus-visible:ring-2 focus-visible:ring-white focus-visible:ring-opacity-75"
      >
        Open dialog
      </button>
    </slot>
  </div>
</div>

<Dialog class="fixed inset-0 z-10 overflow-y-auto" bind:open on:cl={() => (open = false)}>
  <div class="min-h-screen px-4 text-center">
    <div transition:fade={{ duration: 100, easing: cubicInOut }}>
      <DialogOverlay
        class="fixed inset-0 bg-black opacity-40 transition-all cursor-pointer"
        on:click={() => {
          if (clickClose) open = false;
        }}
      />
    </div>

    <!-- {/* This element is to trick the browser into centering the modal contents. */} -->
    <span class="inline-block h-screen align-middle" aria-hidden="true">&#8203;</span>

    <div transition:fade={{ duration: 100, easing: cubicInOut }} class="inline-block p-6 my-8 max-w-7xl overflow-hidden text-left align-middle transition-all transform bg-white shadow-xl rounded-2xl">
      <DialogTitle class="text-lg font-medium leading-6 text-gray-900">{title}</DialogTitle>
      <slot />
    </div>
  </div>
</Dialog>
