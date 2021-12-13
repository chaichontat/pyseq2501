<script lang="ts">
  export let full: number;
  export let curr: number;
</script>

<div class="w-1/2 mt-2 border stats border-base-300">
  <div class="stat">
    <div class="stat-figure text-primary">
      <button class="btn loading btn-circle btn-lg bg-base-200 btn-ghost" />
    </div>
    <div class="stat-value">{`${curr}/${full}`}</div>
    <div class="stat-title">Bundles taken</div>
    <div class="stat-desc">
      <progress value={curr} max={full} class="progress progress-secondary" />
    </div>
  </div>
</div>
