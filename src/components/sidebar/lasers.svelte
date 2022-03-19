<script>
  import { userStore, statusStore } from "$src/stores/store";
  import Laser from "./laser.svelte";
</script>

<li>
  <table class="-mt-6 w-full">
    <colgroup>
      <col style="width:30%" />
      <col style="width:30%" />
      <col style="width:28%" />
      <col style="width:12%" />
    </colgroup>
    <thead class="text-right">
      <tr class="uppercase ">
        <th style="background:transparent" />
        <th class="rounded-l-lg border-r border-r-gray-200 bg-gray-200 text-center text-sm">Target</th>
        <th class="rounded-r-lg bg-gray-200 text-center text-sm">Actual</th>
        <th style="background:transparent" />
      </tr>
    </thead>
    <tbody>
      <Laser name_="532 nm" color="#84cc16" power={$statusStore.lasers[0]} bind:userPower={$userStore.image_params.lasers[0]} />
      <Laser name_="660 nm" color="#ef4444" power={$statusStore.lasers[1]} bind:userPower={$userStore.image_params.lasers[1]} />
    </tbody>
  </table>
</li>

<style lang="postcss">
  th {
    padding-top: 0.5rem;
    padding-bottom: 0.5rem;
  }
</style>
