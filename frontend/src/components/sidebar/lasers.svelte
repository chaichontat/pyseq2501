<script>
  import Laser from "./laser.svelte";

  export let g;
  export let r;
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
        <th class="rounded-l-lg text-right" style="padding-right:0.5rem;">Target</th>
        <th class="rounded-r-lg">Actual</th>
        <th style="background:transparent" />
      </tr>
    </thead>
    <tbody>
      <Laser name="532 nm" color="#84cc16" power={g} />
      <Laser name="633 nm" color="#ef4444" power={r} />
    </tbody>
  </table>
</li>

<style lang="postcss">
  th {
    padding-top: 0.5rem;
    padding-bottom: 0.5rem;
  }
</style>
