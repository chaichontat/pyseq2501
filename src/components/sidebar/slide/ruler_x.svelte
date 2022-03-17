<script lang="ts">
  export const len = 25;

  const cm = Math.floor(len / 10);
  const mm = len % 10;
</script>

<div class="absolute box-border w-full text-sm" style="transform: translateX(-4.25px); width: calc(100% + 1px);">
  {#each [...Array(cm).keys()] as c}
    <div class="cm" style="width: {1000 / len}%; left:{(1000 * c) / len}%;">
      <div class="-translate-x-1.5">{c}</div>
      <div>
        {#each [...Array(10).keys()] as m}
          <div class="mm" style="width: 10%; left:{10 * m}%;" />
        {/each}
      </div>
    </div>
  {/each}

  <div class="cm" style="width: {1000 / len}%; left:{(1000 * cm) / len}%;">
    <div class="translate-x-1">{cm}</div>
    <div>
      {#each [...Array(mm + 1).keys()] as m}
        <div class="mm" style="width: 10%; left:{10 * m}%;" />
      {/each}
    </div>
  </div>
</div>

<style lang="postcss">
  * {
    @apply opacity-90;
  }

  .cm {
    @apply absolute h-4 -translate-y-6 text-left font-mono;
  }
  .mm {
    @apply absolute border-r border-gray-600;
    height: 0.25rem;
    transform: translateY(0.2rem);
  }

  .mm:first-of-type {
    height: 1rem;
  }

  .mm:nth-of-type(6n) {
    height: 0.5rem;
  }
</style>
