<script>
  import Laser from "./laser.svelte";
</script>

<li>
  <table class="table table-fixed w-full" style="margin-top:-0.5rem;">
    <colgroup>
      <col style="width:30%" />
      <col style="width:30%" />
      <col style="width:28%" />
      <col style="width:12%" />
    </colgroup>
    <thead class="text-right">
      <tr>
        <th />
        <th class="text-right" style="padding-right:0.5rem;">Target</th>
        <th>Actual</th>
        <th />
      </tr>
    </thead>
    <tbody>
      <Laser name="532 nm" color="#84cc16" />
      <Laser name="633 nm" color="#ef4444" />
    </tbody>
  </table>
</li>

<style lang="postcss">
  th {
    padding-top: 0.5rem;
    padding-bottom: 0.5rem;
  }
</style>
