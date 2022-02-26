<script lang="ts">
  import Nav from "./nav.svelte";
  import "$src/app.css";
  import "tippy.js/dist/tippy.css";
  import Sidebar from "./sidebar.svelte";

  import { overrideItemIdKeyNameBeforeInitialisingDndZones } from "svelte-dnd-action";
  overrideItemIdKeyNameBeforeInitialisingDndZones("uid");
</script>

<svelte:head>
  <title>PySeq 2501</title>
  <link rel="stylesheet" href="https://rsms.me/inter/inter.css" />
</svelte:head>

<div>
  <div class="drawer drawer-mobile">
    <input id="main-menu" type="checkbox" class="drawer-toggle" />
    <main class="flex-grow block overflow-x-hidden bg-white shadow-md text-base-content drawer-content">
      <Nav />
      <div class="px-10 py-4">
        <slot />
      </div>
    </main>
    <Sidebar />
  </div>
</div>

<style lang="postcss">
  :global(.tippy-box) {
    @apply text-center py-0.5 px-1 rounded-lg opacity-90;
  }

  :global(html) {
    @apply min-w-[1600px];
  }

  .drawer {
    display: grid;
    overflow: hidden;
  }
  .drawer.drawer-end {
    direction: rtl;
  }
  .drawer.drawer-end > * {
    direction: ltr;
  }
  .drawer.drawer-end .drawer-toggle ~ .drawer-side > .drawer-overlay + * {
    justify-self: end;
    --tw-translate-x: 100%;
  }
  .drawer.drawer-end .drawer-toggle:checked ~ .drawer-side > .drawer-overlay + * {
    --tw-translate-x: 0px;
  }
  .drawer.drawer-end .drawer-toggle:checked ~ .drawer-content {
    --tw-translate-x: -0.5rem /* -8px */;
  }

  @media (min-width: 1024px) {
    .drawer-mobile {
      grid-auto-columns: -webkit-max-content auto;
      grid-auto-columns: max-content auto;
    }
    .drawer-mobile > .drawer-toggle ~ .drawer-content {
      height: auto;
    }
    @media (min-width: 1024px) {
      .drawer-mobile > .drawer-toggle ~ .drawer-content {
        grid-column-start: 2;
      }
    }
    @media (min-width: 1024px) {
      .drawer-mobile > .drawer-toggle ~ .drawer-side > .drawer-overlay {
        visibility: visible;
      }
    }
    @media (min-width: 1024px) {
      .drawer-mobile > .drawer-toggle ~ .drawer-side > .drawer-overlay + * {
        --tw-translate-x: 0px;
      }
    }
    @media (min-width: 1024px) {
      .drawer-mobile.drawer-end > .drawer-toggle ~ .drawer-content {
        grid-column-start: 1;
      }
    }
    @media (min-width: 1024px) {
      .drawer-mobile.drawer-end > .drawer-toggle ~ .drawer-side {
        grid-column-start: 2;
      }
    }
    @media (min-width: 1024px) {
      .drawer-mobile.drawer-end > .drawer-toggle ~ .drawer-side > .drawer-overlay {
        visibility: visible;
      }
    }
    @media (min-width: 1024px) {
      .drawer-mobile.drawer-end > .drawer-toggle ~ .drawer-side > .drawer-overlay + * {
        --tw-translate-x: 0px;
      }
    }
    .drawer-mobile > .drawer-toggle ~ .drawer-side {
      overflow-y: auto;
    }
    .drawer-mobile.drawer-end {
      grid-auto-columns: auto -webkit-max-content;
      grid-auto-columns: auto max-content;
      direction: ltr;
    }
    .drawer-mobile.drawer-end > .drawer-toggle ~ .drawer-content {
      height: auto;
    }
    .drawer-mobile.drawer-end > .drawer-toggle ~ .drawer-side {
      overflow-y: auto;
    }
  }
  @media (min-width: 1024px) {
    .drawer-mobile {
      grid-auto-columns: -webkit-max-content auto;
      grid-auto-columns: max-content auto;
    }
    .drawer-mobile > .drawer-toggle ~ .drawer-content {
      height: auto;
    }
    @media (min-width: 1024px) {
      .drawer-mobile > .drawer-toggle ~ .drawer-content {
        grid-column-start: 2;
      }
    }
    @media (min-width: 1024px) {
      .drawer-mobile > .drawer-toggle ~ .drawer-side > .drawer-overlay {
        visibility: visible;
      }
    }
    @media (min-width: 1024px) {
      .drawer-mobile > .drawer-toggle ~ .drawer-side > .drawer-overlay + * {
        --tw-translate-x: 0px;
      }
    }
    @media (min-width: 1024px) {
      .drawer-mobile.drawer-end > .drawer-toggle ~ .drawer-content {
        grid-column-start: 1;
      }
    }
    @media (min-width: 1024px) {
      .drawer-mobile.drawer-end > .drawer-toggle ~ .drawer-side {
        grid-column-start: 2;
      }
    }
    @media (min-width: 1024px) {
      .drawer-mobile.drawer-end > .drawer-toggle ~ .drawer-side > .drawer-overlay {
        visibility: visible;
      }
    }
    @media (min-width: 1024px) {
      .drawer-mobile.drawer-end > .drawer-toggle ~ .drawer-side > .drawer-overlay + * {
        --tw-translate-x: 0px;
      }
    }
    .drawer-mobile > .drawer-toggle ~ .drawer-side {
      overflow-y: auto;
    }
    .drawer-mobile.drawer-end {
      grid-auto-columns: auto -webkit-max-content;
      grid-auto-columns: auto max-content;
      direction: ltr;
    }
    .drawer-mobile.drawer-end > .drawer-toggle ~ .drawer-content {
      height: auto;
    }
    .drawer-mobile.drawer-end > .drawer-toggle ~ .drawer-side {
      overflow-y: auto;
    }
  }
  @media (min-width: 1024px) {
    .drawer-mobile {
      grid-auto-columns: -webkit-max-content auto;
      grid-auto-columns: max-content auto;
    }
    .drawer-mobile > .drawer-toggle ~ .drawer-content {
      height: auto;
    }
    @media (min-width: 1024px) {
      .drawer-mobile > .drawer-toggle ~ .drawer-content {
        grid-column-start: 2;
      }
    }
    @media (min-width: 1024px) {
      .drawer-mobile > .drawer-toggle ~ .drawer-side > .drawer-overlay {
        visibility: visible;
      }
    }
    @media (min-width: 1024px) {
      .drawer-mobile > .drawer-toggle ~ .drawer-side > .drawer-overlay + * {
        --tw-translate-x: 0px;
      }
    }
    @media (min-width: 1024px) {
      .drawer-mobile.drawer-end > .drawer-toggle ~ .drawer-content {
        grid-column-start: 1;
      }
    }
    @media (min-width: 1024px) {
      .drawer-mobile.drawer-end > .drawer-toggle ~ .drawer-side {
        grid-column-start: 2;
      }
    }
    @media (min-width: 1024px) {
      .drawer-mobile.drawer-end > .drawer-toggle ~ .drawer-side > .drawer-overlay {
        visibility: visible;
      }
    }
    @media (min-width: 1024px) {
      .drawer-mobile.drawer-end > .drawer-toggle ~ .drawer-side > .drawer-overlay + * {
        --tw-translate-x: 0px;
      }
    }
    .drawer-mobile > .drawer-toggle ~ .drawer-side {
      overflow-y: auto;
    }
    .drawer-mobile.drawer-end {
      grid-auto-columns: auto -webkit-max-content;
      grid-auto-columns: auto max-content;
      direction: ltr;
    }
    .drawer-mobile.drawer-end > .drawer-toggle ~ .drawer-content {
      height: auto;
    }
    .drawer-mobile.drawer-end > .drawer-toggle ~ .drawer-side {
      overflow-y: auto;
    }
  }
  @media (min-width: 1024px) {
    .drawer-mobile {
      grid-auto-columns: -webkit-max-content auto;
      grid-auto-columns: max-content auto;
    }
    .drawer-mobile > .drawer-toggle ~ .drawer-content {
      height: auto;
    }
    @media (min-width: 1024px) {
      .drawer-mobile > .drawer-toggle ~ .drawer-content {
        grid-column-start: 2;
      }
    }
    @media (min-width: 1024px) {
      .drawer-mobile > .drawer-toggle ~ .drawer-side > .drawer-overlay {
        visibility: visible;
      }
    }
    @media (min-width: 1024px) {
      .drawer-mobile > .drawer-toggle ~ .drawer-side > .drawer-overlay + * {
        --tw-translate-x: 0px;
      }
    }
    @media (min-width: 1024px) {
      .drawer-mobile.drawer-end > .drawer-toggle ~ .drawer-content {
        grid-column-start: 1;
      }
    }
    @media (min-width: 1024px) {
      .drawer-mobile.drawer-end > .drawer-toggle ~ .drawer-side {
        grid-column-start: 2;
      }
    }
    @media (min-width: 1024px) {
      .drawer-mobile.drawer-end > .drawer-toggle ~ .drawer-side > .drawer-overlay {
        visibility: visible;
      }
    }
    @media (min-width: 1024px) {
      .drawer-mobile.drawer-end > .drawer-toggle ~ .drawer-side > .drawer-overlay + * {
        --tw-translate-x: 0px;
      }
    }
    .drawer-mobile > .drawer-toggle ~ .drawer-side {
      overflow-y: auto;
    }
    .drawer-mobile.drawer-end {
      grid-auto-columns: auto -webkit-max-content;
      grid-auto-columns: auto max-content;
      direction: ltr;
    }
    .drawer-mobile.drawer-end > .drawer-toggle ~ .drawer-content {
      height: auto;
    }
    .drawer-mobile.drawer-end > .drawer-toggle ~ .drawer-side {
      overflow-y: auto;
    }
  }
  @media (min-width: 1024px) {
    .drawer-mobile {
      grid-auto-columns: -webkit-max-content auto;
      grid-auto-columns: max-content auto;
    }
    .drawer-mobile > .drawer-toggle ~ .drawer-content {
      height: auto;
    }
    @media (min-width: 1024px) {
      .drawer-mobile > .drawer-toggle ~ .drawer-content {
        grid-column-start: 2;
      }
    }
    @media (min-width: 1024px) {
      .drawer-mobile > .drawer-toggle ~ .drawer-side > .drawer-overlay {
        visibility: visible;
      }
    }
    @media (min-width: 1024px) {
      .drawer-mobile > .drawer-toggle ~ .drawer-side > .drawer-overlay + * {
        --tw-translate-x: 0px;
      }
    }
    @media (min-width: 1024px) {
      .drawer-mobile.drawer-end > .drawer-toggle ~ .drawer-content {
        grid-column-start: 1;
      }
    }
    @media (min-width: 1024px) {
      .drawer-mobile.drawer-end > .drawer-toggle ~ .drawer-side {
        grid-column-start: 2;
      }
    }
    @media (min-width: 1024px) {
      .drawer-mobile.drawer-end > .drawer-toggle ~ .drawer-side > .drawer-overlay {
        visibility: visible;
      }
    }
    @media (min-width: 1024px) {
      .drawer-mobile.drawer-end > .drawer-toggle ~ .drawer-side > .drawer-overlay + * {
        --tw-translate-x: 0px;
      }
    }
    .drawer-mobile > .drawer-toggle ~ .drawer-side {
      overflow-y: auto;
    }
    .drawer-mobile.drawer-end {
      grid-auto-columns: auto -webkit-max-content;
      grid-auto-columns: auto max-content;
      direction: ltr;
    }
    .drawer-mobile.drawer-end > .drawer-toggle ~ .drawer-content {
      height: auto;
    }
    .drawer-mobile.drawer-end > .drawer-toggle ~ .drawer-side {
      overflow-y: auto;
    }
  }
  @media (min-width: 1024px) {
    .drawer-mobile {
      grid-auto-columns: -webkit-max-content auto;
      grid-auto-columns: max-content auto;
    }
    .drawer-mobile > .drawer-toggle ~ .drawer-content {
      height: auto;
    }
    @media (min-width: 1024px) {
      .drawer-mobile > .drawer-toggle ~ .drawer-content {
        grid-column-start: 2;
      }
    }
    @media (min-width: 1024px) {
      .drawer-mobile > .drawer-toggle ~ .drawer-side > .drawer-overlay {
        visibility: visible;
      }
    }
    @media (min-width: 1024px) {
      .drawer-mobile > .drawer-toggle ~ .drawer-side > .drawer-overlay + * {
        --tw-translate-x: 0px;
      }
    }
    @media (min-width: 1024px) {
      .drawer-mobile.drawer-end > .drawer-toggle ~ .drawer-content {
        grid-column-start: 1;
      }
    }
    @media (min-width: 1024px) {
      .drawer-mobile.drawer-end > .drawer-toggle ~ .drawer-side {
        grid-column-start: 2;
      }
    }
    @media (min-width: 1024px) {
      .drawer-mobile.drawer-end > .drawer-toggle ~ .drawer-side > .drawer-overlay {
        visibility: visible;
      }
    }
    @media (min-width: 1024px) {
      .drawer-mobile.drawer-end > .drawer-toggle ~ .drawer-side > .drawer-overlay + * {
        --tw-translate-x: 0px;
      }
    }
    .drawer-mobile > .drawer-toggle ~ .drawer-side {
      overflow-y: auto;
    }
    .drawer-mobile.drawer-end {
      grid-auto-columns: auto -webkit-max-content;
      grid-auto-columns: auto max-content;
      direction: ltr;
    }
    .drawer-mobile.drawer-end > .drawer-toggle ~ .drawer-content {
      height: auto;
    }
    .drawer-mobile.drawer-end > .drawer-toggle ~ .drawer-side {
      overflow-y: auto;
    }
  }
  @media (min-width: 1024px) {
    .drawer-mobile {
      grid-auto-columns: -webkit-max-content auto;
      grid-auto-columns: max-content auto;
    }
    .drawer-mobile > .drawer-toggle ~ .drawer-content {
      height: auto;
    }
    @media (min-width: 1024px) {
      .drawer-mobile > .drawer-toggle ~ .drawer-content {
        grid-column-start: 2;
      }
    }
    @media (min-width: 1024px) {
      .drawer-mobile > .drawer-toggle ~ .drawer-side > .drawer-overlay {
        visibility: visible;
      }
    }
    @media (min-width: 1024px) {
      .drawer-mobile > .drawer-toggle ~ .drawer-side > .drawer-overlay + * {
        --tw-translate-x: 0px;
      }
    }
    @media (min-width: 1024px) {
      .drawer-mobile.drawer-end > .drawer-toggle ~ .drawer-content {
        grid-column-start: 1;
      }
    }
    @media (min-width: 1024px) {
      .drawer-mobile.drawer-end > .drawer-toggle ~ .drawer-side {
        grid-column-start: 2;
      }
    }
    @media (min-width: 1024px) {
      .drawer-mobile.drawer-end > .drawer-toggle ~ .drawer-side > .drawer-overlay {
        visibility: visible;
      }
    }
    @media (min-width: 1024px) {
      .drawer-mobile.drawer-end > .drawer-toggle ~ .drawer-side > .drawer-overlay + * {
        --tw-translate-x: 0px;
      }
    }
    .drawer-mobile > .drawer-toggle ~ .drawer-side {
      overflow-y: auto;
    }
    .drawer-mobile.drawer-end {
      grid-auto-columns: auto -webkit-max-content;
      grid-auto-columns: auto max-content;
      direction: ltr;
    }
    .drawer-mobile.drawer-end > .drawer-toggle ~ .drawer-content {
      height: auto;
    }
    .drawer-mobile.drawer-end > .drawer-toggle ~ .drawer-side {
      overflow-y: auto;
    }
  }
  @media (min-width: 1024px) {
    .drawer-mobile {
      grid-auto-columns: -webkit-max-content auto;
      grid-auto-columns: max-content auto;
    }
    .drawer-mobile > .drawer-toggle ~ .drawer-content {
      height: auto;
    }
    @media (min-width: 1024px) {
      .drawer-mobile > .drawer-toggle ~ .drawer-content {
        grid-column-start: 2;
      }
    }
    @media (min-width: 1024px) {
      .drawer-mobile > .drawer-toggle ~ .drawer-side > .drawer-overlay {
        visibility: visible;
      }
    }
    @media (min-width: 1024px) {
      .drawer-mobile > .drawer-toggle ~ .drawer-side > .drawer-overlay + * {
        --tw-translate-x: 0px;
      }
    }
    @media (min-width: 1024px) {
      .drawer-mobile.drawer-end > .drawer-toggle ~ .drawer-content {
        grid-column-start: 1;
      }
    }
    @media (min-width: 1024px) {
      .drawer-mobile.drawer-end > .drawer-toggle ~ .drawer-side {
        grid-column-start: 2;
      }
    }
    @media (min-width: 1024px) {
      .drawer-mobile.drawer-end > .drawer-toggle ~ .drawer-side > .drawer-overlay {
        visibility: visible;
      }
    }
    @media (min-width: 1024px) {
      .drawer-mobile.drawer-end > .drawer-toggle ~ .drawer-side > .drawer-overlay + * {
        --tw-translate-x: 0px;
      }
    }
    .drawer-mobile > .drawer-toggle ~ .drawer-side {
      overflow-y: auto;
    }
    .drawer-mobile.drawer-end {
      grid-auto-columns: auto -webkit-max-content;
      grid-auto-columns: auto max-content;
      direction: ltr;
    }
    .drawer-mobile.drawer-end > .drawer-toggle ~ .drawer-content {
      height: auto;
    }
    .drawer-mobile.drawer-end > .drawer-toggle ~ .drawer-side {
      overflow-y: auto;
    }
  }
  @media (min-width: 1024px) {
    .drawer-mobile {
      grid-auto-columns: -webkit-max-content auto;
      grid-auto-columns: max-content auto;
    }
    .drawer-mobile > .drawer-toggle ~ .drawer-content {
      height: auto;
    }
    @media (min-width: 1024px) {
      .drawer-mobile > .drawer-toggle ~ .drawer-content {
        grid-column-start: 2;
      }
    }
    @media (min-width: 1024px) {
      .drawer-mobile > .drawer-toggle ~ .drawer-side > .drawer-overlay {
        visibility: visible;
      }
    }
    @media (min-width: 1024px) {
      .drawer-mobile > .drawer-toggle ~ .drawer-side > .drawer-overlay + * {
        --tw-translate-x: 0px;
      }
    }
    @media (min-width: 1024px) {
      .drawer-mobile.drawer-end > .drawer-toggle ~ .drawer-content {
        grid-column-start: 1;
      }
    }
    @media (min-width: 1024px) {
      .drawer-mobile.drawer-end > .drawer-toggle ~ .drawer-side {
        grid-column-start: 2;
      }
    }
    @media (min-width: 1024px) {
      .drawer-mobile.drawer-end > .drawer-toggle ~ .drawer-side > .drawer-overlay {
        visibility: visible;
      }
    }
    @media (min-width: 1024px) {
      .drawer-mobile.drawer-end > .drawer-toggle ~ .drawer-side > .drawer-overlay + * {
        --tw-translate-x: 0px;
      }
    }
    .drawer-mobile > .drawer-toggle ~ .drawer-side {
      overflow-y: auto;
    }
    .drawer-mobile.drawer-end {
      grid-auto-columns: auto -webkit-max-content;
      grid-auto-columns: auto max-content;
      direction: ltr;
    }
    .drawer-mobile.drawer-end > .drawer-toggle ~ .drawer-content {
      height: auto;
    }
    .drawer-mobile.drawer-end > .drawer-toggle ~ .drawer-side {
      overflow-y: auto;
    }
  }
  @media (min-width: 1024px) {
    .drawer-mobile {
      grid-auto-columns: -webkit-max-content auto;
      grid-auto-columns: max-content auto;
    }
    .drawer-mobile > .drawer-toggle ~ .drawer-content {
      height: auto;
    }
    @media (min-width: 1024px) {
      .drawer-mobile > .drawer-toggle ~ .drawer-content {
        grid-column-start: 2;
      }
    }
    @media (min-width: 1024px) {
      .drawer-mobile > .drawer-toggle ~ .drawer-side > .drawer-overlay {
        visibility: visible;
      }
    }
    @media (min-width: 1024px) {
      .drawer-mobile > .drawer-toggle ~ .drawer-side > .drawer-overlay + * {
        --tw-translate-x: 0px;
      }
    }
    @media (min-width: 1024px) {
      .drawer-mobile.drawer-end > .drawer-toggle ~ .drawer-content {
        grid-column-start: 1;
      }
    }
    @media (min-width: 1024px) {
      .drawer-mobile.drawer-end > .drawer-toggle ~ .drawer-side {
        grid-column-start: 2;
      }
    }
    @media (min-width: 1024px) {
      .drawer-mobile.drawer-end > .drawer-toggle ~ .drawer-side > .drawer-overlay {
        visibility: visible;
      }
    }
    @media (min-width: 1024px) {
      .drawer-mobile.drawer-end > .drawer-toggle ~ .drawer-side > .drawer-overlay + * {
        --tw-translate-x: 0px;
      }
    }
    .drawer-mobile > .drawer-toggle ~ .drawer-side {
      overflow-y: auto;
    }
    .drawer-mobile.drawer-end {
      grid-auto-columns: auto -webkit-max-content;
      grid-auto-columns: auto max-content;
      direction: ltr;
    }
    .drawer-mobile.drawer-end > .drawer-toggle ~ .drawer-content {
      height: auto;
    }
    .drawer-mobile.drawer-end > .drawer-toggle ~ .drawer-side {
      overflow-y: auto;
    }
  }
  @media (min-width: 1024px) {
    .drawer-mobile {
      grid-auto-columns: -webkit-max-content auto;
      grid-auto-columns: max-content auto;
    }
    .drawer-mobile > .drawer-toggle ~ .drawer-content {
      height: auto;
    }
    @media (min-width: 1024px) {
      .drawer-mobile > .drawer-toggle ~ .drawer-content {
        grid-column-start: 2;
      }
    }
    @media (min-width: 1024px) {
      .drawer-mobile > .drawer-toggle ~ .drawer-side > .drawer-overlay {
        visibility: visible;
      }
    }
    @media (min-width: 1024px) {
      .drawer-mobile > .drawer-toggle ~ .drawer-side > .drawer-overlay + * {
        --tw-translate-x: 0px;
      }
    }
    @media (min-width: 1024px) {
      .drawer-mobile.drawer-end > .drawer-toggle ~ .drawer-content {
        grid-column-start: 1;
      }
    }
    @media (min-width: 1024px) {
      .drawer-mobile.drawer-end > .drawer-toggle ~ .drawer-side {
        grid-column-start: 2;
      }
    }
    @media (min-width: 1024px) {
      .drawer-mobile.drawer-end > .drawer-toggle ~ .drawer-side > .drawer-overlay {
        visibility: visible;
      }
    }
    @media (min-width: 1024px) {
      .drawer-mobile.drawer-end > .drawer-toggle ~ .drawer-side > .drawer-overlay + * {
        --tw-translate-x: 0px;
      }
    }
    .drawer-mobile > .drawer-toggle ~ .drawer-side {
      overflow-y: auto;
    }
    .drawer-mobile.drawer-end {
      grid-auto-columns: auto -webkit-max-content;
      grid-auto-columns: auto max-content;
      direction: ltr;
    }
    .drawer-mobile.drawer-end > .drawer-toggle ~ .drawer-content {
      height: auto;
    }
    .drawer-mobile.drawer-end > .drawer-toggle ~ .drawer-side {
      overflow-y: auto;
    }
  }
  @media (min-width: 1024px) {
    .drawer-mobile {
      grid-auto-columns: -webkit-max-content auto;
      grid-auto-columns: max-content auto;
    }
    .drawer-mobile > .drawer-toggle ~ .drawer-content {
      height: auto;
    }
    @media (min-width: 1024px) {
      .drawer-mobile > .drawer-toggle ~ .drawer-content {
        grid-column-start: 2;
      }
    }
    @media (min-width: 1024px) {
      .drawer-mobile > .drawer-toggle ~ .drawer-side > .drawer-overlay {
        visibility: visible;
      }
    }
    @media (min-width: 1024px) {
      .drawer-mobile > .drawer-toggle ~ .drawer-side > .drawer-overlay + * {
        --tw-translate-x: 0px;
      }
    }
    @media (min-width: 1024px) {
      .drawer-mobile.drawer-end > .drawer-toggle ~ .drawer-content {
        grid-column-start: 1;
      }
    }
    @media (min-width: 1024px) {
      .drawer-mobile.drawer-end > .drawer-toggle ~ .drawer-side {
        grid-column-start: 2;
      }
    }
    @media (min-width: 1024px) {
      .drawer-mobile.drawer-end > .drawer-toggle ~ .drawer-side > .drawer-overlay {
        visibility: visible;
      }
    }
    @media (min-width: 1024px) {
      .drawer-mobile.drawer-end > .drawer-toggle ~ .drawer-side > .drawer-overlay + * {
        --tw-translate-x: 0px;
      }
    }
    .drawer-mobile > .drawer-toggle ~ .drawer-side {
      overflow-y: auto;
    }
    .drawer-mobile.drawer-end {
      grid-auto-columns: auto -webkit-max-content;
      grid-auto-columns: auto max-content;
      direction: ltr;
    }
    .drawer-mobile.drawer-end > .drawer-toggle ~ .drawer-content {
      height: auto;
    }
    .drawer-mobile.drawer-end > .drawer-toggle ~ .drawer-side {
      overflow-y: auto;
    }
  }
  @media (min-width: 1024px) {
    .drawer-mobile {
      grid-auto-columns: -webkit-max-content auto;
      grid-auto-columns: max-content auto;
    }
    .drawer-mobile > .drawer-toggle ~ .drawer-content {
      height: auto;
    }
    @media (min-width: 1024px) {
      .drawer-mobile > .drawer-toggle ~ .drawer-content {
        grid-column-start: 2;
      }
    }
    @media (min-width: 1024px) {
      .drawer-mobile > .drawer-toggle ~ .drawer-side > .drawer-overlay {
        visibility: visible;
      }
    }
    @media (min-width: 1024px) {
      .drawer-mobile > .drawer-toggle ~ .drawer-side > .drawer-overlay + * {
        --tw-translate-x: 0px;
      }
    }
    @media (min-width: 1024px) {
      .drawer-mobile.drawer-end > .drawer-toggle ~ .drawer-content {
        grid-column-start: 1;
      }
    }
    @media (min-width: 1024px) {
      .drawer-mobile.drawer-end > .drawer-toggle ~ .drawer-side {
        grid-column-start: 2;
      }
    }
    @media (min-width: 1024px) {
      .drawer-mobile.drawer-end > .drawer-toggle ~ .drawer-side > .drawer-overlay {
        visibility: visible;
      }
    }
    @media (min-width: 1024px) {
      .drawer-mobile.drawer-end > .drawer-toggle ~ .drawer-side > .drawer-overlay + * {
        --tw-translate-x: 0px;
      }
    }
    .drawer-mobile > .drawer-toggle ~ .drawer-side {
      overflow-y: auto;
    }
    .drawer-mobile.drawer-end {
      grid-auto-columns: auto -webkit-max-content;
      grid-auto-columns: auto max-content;
      direction: ltr;
    }
    .drawer-mobile.drawer-end > .drawer-toggle ~ .drawer-content {
      height: auto;
    }
    .drawer-mobile.drawer-end > .drawer-toggle ~ .drawer-side {
      overflow-y: auto;
    }
  }
  @media (min-width: 1024px) {
    .drawer-mobile > .drawer-toggle:checked ~ .drawer-content {
      --tw-translate-x: 0px;
    }
  }
</style>
