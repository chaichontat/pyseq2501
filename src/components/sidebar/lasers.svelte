<script>
  import { userStore, statusStore } from "$src/store";
  import Laser from "./laser.svelte";
</script>

<li>
  <table class="table table-fixed w-full" style="margin-top:-1.5rem;">
    <colgroup>
      <col style="width:30%" />
      <col style="width:30%" />
      <col style="width:28%" />
      <col style="width:12%" />
    </colgroup>
    <thead class="text-right">
      <tr>
        <th style="background:transparent" />
        <th class="rounded-l-lg text-center text-sm">Target</th>
        <th class="rounded-r-lg text-center text-sm">Actual</th>
        <th style="background:transparent" />
      </tr>
    </thead>
    <tbody>
      <Laser
        name="532 nm"
        color="#84cc16"
        power={$statusStore.laser_g}
        userPower={$userStore.laser_g}
      />
      <Laser
        name="633 nm"
        color="#ef4444"
        power={$statusStore.laser_r}
        userPower={$userStore.laser_r}
      />
    </tbody>
  </table>
</li>

<style lang="postcss">
  th {
    padding-top: 0.5rem;
    padding-bottom: 0.5rem;
  }
</style>
