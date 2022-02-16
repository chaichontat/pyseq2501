<script lang="ts">
  import Preview from "$comps/main/preview.svelte";
  import { userStore as us } from "$src/store";
  import ProgressManual from "$src/components/main/manual/progress_manual.svelte";
  import Details from "$src/components/main/auto/details.svelte";
  import Setxy from "$src/components/main/auto/steps/setxy.svelte";
  import XYInput from "$comps/main/xy_input.svelte";

  let height = 0;

  $: height = (128 * 0.375) / 1000;
</script>

<div class="box-border sticky z-40 -mx-10 px-10 pb-6 shadow-md bg-white/[0.95] border-b top-16 ">
  <div class="w-full h-4" />
  <ProgressManual />
</div>

<p class="mt-6 title">Capture Parameters</p>
<!-- Capture params. -->
<div class="grid grid-cols-2 gap-y-6 gap-x-4">
  <section class="flex flex-col text-lg font-medium">
    <p class="text-lg">Name</p>
    <input type="text" class="max-w-md mt-1 mb-4 pretty" bind:value={$us.image_params.name} />

    <p class="text-lg">Image Path</p>
    <input type="text" class="max-w-md mt-1 mb-4 pretty" bind:value={$us.image_params.path} />
  </section>

  <!-- Optics -->
  <section class="font-medium leading-10">
    <h2 class="">Laser and Channels</h2>
    <div class="grid grid-cols-2">
      <p class="flex flex-col">
        <span class:text-gray-400={!$us.image_params.laser_onoff[0]}>
          <label>
            <input type="checkbox" class="mr-1 rounded text-lime-500 focus:ring-lime-300" bind:checked={$us.image_params.laser_onoff[0]} />
            <div class="inline">
              Laser:
              <div class="inline" class:text-green-800={$us.image_params.laser_onoff[0]}>532 nm</div>
            </div>
          </label>
          <input
            type="number"
            class="w-20 h-8 mr-1 pretty"
            class:pretty-disabled={!$us.image_params.laser_onoff[0]}
            bind:value={$us.image_params.lasers[1]}
            disabled={!$us.image_params.laser_onoff[0]}
          />
          mW
        </span>

        <label class="rounded-lg channel ring-red-500" class:text-gray-400={!$us.image_params.channels[0]}>
          <input type="checkbox" class="mr-1 text-green-500 rounded focus:ring-green-300" bind:checked={$us.image_params.channels[0]} />
          Channel 0
        </label>

        <label class="channel" class:text-gray-400={!$us.image_params.channels[1]}>
          <input type="checkbox" class="mr-1 text-orange-600 rounded focus:ring-orange-300" bind:checked={$us.image_params.channels[1]} />
          Channel 1
        </label>
      </p>

      <p class="flex flex-col">
        <span class:text-gray-400={!$us.image_params.laser_onoff[1]}>
          <label class="whitespace-nowrap">
            <input type="checkbox" class="mr-1 text-red-600 rounded focus:ring-red-300" bind:checked={$us.image_params.laser_onoff[1]} />
            Laser:
            <div class="inline" class:text-red-800={$us.image_params.laser_onoff[1]}>660 nm</div>
          </label>
          <input
            type="number"
            class="w-20 h-8 mr-1 pretty"
            class:pretty-disabled={!$us.image_params.laser_onoff[1]}
            bind:value={$us.image_params.lasers[1]}
            disabled={$us.image_params.laser_onoff[1]}
          />
          mW
        </span>
        <label class="channel" class:text-gray-500={!$us.image_params.channels[2]}>
          <input type="checkbox" class="mr-1 rounded text-rose-700 focus:ring-rose-500" bind:checked={$us.image_params.channels[2]} />
          Channel 2
        </label>
        <label class="channel" class:text-gray-500={!$us.image_params.channels[3]}>
          <input type="checkbox" class="mr-1 rounded text-amber-900 focus:ring-amber-700" bind:checked={$us.image_params.channels[3]} />
          Channel 3
        </label>
      </p>
    </div>
  </section>

  <!-- XY Input -->
  <section class="flex flex-col gap-2">
    <h2 class="mb-1 text-xl font-semibold">Positions</h2>
    <div class="mb-1">
      <p class="mb-1">📌 Corner 1</p>
      <XYInput bind:xy={$us.image_params.xy0} />
    </div>
    <div>
      <p class="mb-1">📍 Corner 2</p>
      <XYInput bind:xy={$us.image_params.xy1} />
    </div>
  </section>

  <!-- Focus stuffs -->
  <section class="flex flex-col gap-2">
    <h2 class="">Focus</h2>

    Z Tilt
    <input type="number" class="w-28 pretty" bind:value={$us.image_params.z_tilt} />

    Z Objective
    <span class="flex gap-2">
      <input type="number" class="w-28 pretty" bind:value={$us.image_params.z_obj} />
      <button type="button" class="px-4 py-1 font-medium text-gray-900 rounded-lg h-11 w-36 white-button">
        <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 mr-1" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clip-rule="evenodd" />
        </svg>
        <span>Autofocus</span>
      </button>
    </span>
  </section>
</div>

<p class="title">Preview</p>
<Preview />

<style lang="postcss">
  h2 {
    @apply mb-1 text-xl font-semibold text-gray-800;
  }
  .channel {
    @apply text-base ml-8;
  }
</style>
