<script lang="ts">
  import type { TakeImage } from "$src/stores/command";

  import { userStore as us } from "$src/stores/store";
  export let params: TakeImage;
  export let i: 0 | 1;

  function transformOD(e: Event & { currentTarget: EventTarget & HTMLSelectElement }) {
    let res;
    switch (e.currentTarget.value) {
      case "Open":
        res = 0;
        break;
      case "Closed":
        res = -1;
        break;
      default:
        res = Number(e.currentTarget.value);
    }
    params.od[i] = res;
  }
</script>

<p class="flex flex-col">
  <!-- Green -->
  <span class:text-gray-400={!params.laser_onoff[i]}>
    <label>
      <input type="checkbox" class={`mr-1 rounded ${i ? "text-red-600 rounded focus:ring-red-300" : "text-lime-500 focus:ring-lime-300"}`} bind:checked={params.laser_onoff[i]} />
      <div class="inline" class:text-green-800={params.laser_onoff[i]}>{Boolean(i) ? 660 : 532} nm</div>
    </label>
    <input type="number" class="w-20 h-8 mr-1 pretty" class:pretty-disabled={!params.laser_onoff[0]} bind:value={params.lasers[i]} disabled={!params.laser_onoff[i]} />
    mW
  </span>

  <label class="rounded-lg channel ring-red-500" class:text-gray-400={!params.channels[2 * i]}>
    <input type="checkbox" class={`mr-1 rounded ${i ? "text-rose-700 focus:ring-rose-500" : "text-green-500 focus:ring-green-300"}`} bind:checked={params.channels[2 * i]} />
    Channel {2 * i}
  </label>

  <label class="channel" class:text-gray-400={!params.channels[2 * i + 1]}>
    <input type="checkbox" class={`mr-1 rounded ${i ? "text-amber-900 focus:ring-amber-700" : "text-orange-600 rounded focus:ring-orange-300"}`} bind:checked={params.channels[2 * i + 1]} />
    Channel {2 * i + 1}
  </label>

  <span class="ml-8 font-normal opacity-85">
    Filter OD
    <select class="py-1 text-sm border-gray-400 rounded disabled:border-gray-300" on:change={transformOD}>
      {#if i == 0}
        <option>Open</option>
        <option>1.0</option>
        <option>2.0</option>
        <option>3.5</option>
        <option>3.8</option>
        <option>4.0</option>
        <option>4.5</option>
        <option>Closed</option>
      {:else}
        <option>Open</option>
        <option>0.2</option>
        <option>0.5</option>
        <option>0.6</option>
        <option>1.0</option>
        <option>2.4</option>
        <option>4.0</option>
        <option>Closed</option>
      {/if}
    </select>
    <p class="text-sm font-medium ml-3">Effective: {(Number(params.od[i] != -1) * params.lasers[i] * Math.pow(10, -params.od[i])).toFixed(4)} mW</p>
  </span>
</p>

<style lang="postcss">
  .channel {
    @apply text-base ml-8;
  }
</style>
