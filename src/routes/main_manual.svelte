<script lang="ts">
  import Preview from "$comps/main/preview.svelte";
  import { userStore as us } from "$src/store";
  import ProgressManual from "$src/components/main/manual/progress_manual.svelte";
  import Details from "$src/components/main/auto/details.svelte";
</script>

<ProgressManual />

<p class="title">Capture Parameters</p>
<!-- Capture params. -->
<div class="grid grid-cols-2">
  <div>
    <Details />
  </div>

  <div class="grid grid-cols-2 font-medium">
    <div id="green">
      532nm
      <ol>
        <li class="channel" class:text-gray-500={!$us.man_params.channels[0]}>
          <input type="checkbox" class="mr-1 text-green-500 rounded focus:ring-green-300" bind:checked={$us.man_params.channels[0]} />
          Channel 0
        </li>
        <li class="channel" class:text-gray-500={!$us.man_params.channels[1]}>
          <input type="checkbox" class="mr-1 text-orange-600 rounded focus:ring-orange-300" bind:checked={$us.man_params.channels[1]} />
          Channel 1
        </li>
      </ol>
    </div>
    <div id="red">
      633nm
      <ol>
        <li class="channel" class:text-gray-500={!$us.man_params.channels[2]}>
          <input type="checkbox" class="mr-1 rounded text-rose-700 focus:ring-rose-500" bind:checked={$us.man_params.channels[2]} />
          Channel 2
        </li>
        <li class="channel" class:text-gray-500={!$us.man_params.channels[3]}>
          <input type="checkbox" class="mr-1 rounded text-amber-900 focus:ring-amber-700" bind:checked={$us.man_params.channels[3]} />
          Channel 3
        </li>
      </ol>
    </div>
  </div>
</div>

<p class="title">Preview</p>
<Preview />
