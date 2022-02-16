<script>
  import { userStore, statusStore } from "$src/store";
  import Laser from "./laser.svelte";
</script>

<li>
  <table class="w-full -mt-6">
    <colgroup>
      <col style="width:30%" />
      <col style="width:30%" />
      <col style="width:28%" />
      <col style="width:12%" />
    </colgroup>
    <thead class="text-right">
      <tr class="uppercase ">
        <th style="background:transparent" />
        <th class="text-sm text-center bg-gray-200 border-r rounded-l-lg border-r-gray-200">Target</th>
        <th class="text-sm text-center bg-gray-200 rounded-r-lg">Actual</th>
        <th style="background:transparent" />
      </tr>
    </thead>
    <tbody>
      <Laser name="532 nm" color="#84cc16" power={$statusStore.laser_g} bind:userPower={$userStore.image_params.lasers[0]} />
      <Laser name="660 nm" color="#ef4444" power={$statusStore.laser_r} bind:userPower={$userStore.image_params.lasers[1]} />
    </tbody>
  </table>
</li>

<style lang="postcss">
  th {
    padding-top: 0.5rem;
    padding-bottom: 0.5rem;
  }
</style>
