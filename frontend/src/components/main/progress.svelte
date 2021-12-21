<script lang="ts">
  export let full: null | number;
  export let curr: null | number;

  let _curr = "--";
  let _full = "--";

  $: {
    _full = full ? full.toString() : "--";
    _curr = curr ? curr.toString() : "--";
  }
</script>

<div class="w-1/2 mt-2 border stats border-base-300">
  <div class="stat">
    <div class="stat-figure text-primary">
      <button class="btn loading btn-circle btn-lg bg-base-200 btn-ghost" />
    </div>
    <div class="stat-value">{`${_curr}/${_full}`}</div>
    <div class="stat-title">Bundles taken</div>
    <div class="stat-desc">
      <progress value={curr} max={full} class="progress progress-secondary" />
    </div>
  </div>
</div>
