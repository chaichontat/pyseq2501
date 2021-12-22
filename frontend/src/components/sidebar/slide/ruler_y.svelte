<script lang="ts">
  export const len = 75;

  const cm = Math.floor(len / 10);
  const mm = len % 10;
</script>

<div
  class="box-border absolute left-full text-sm"
  style="transform: translateY(-1px); height: calc(100% + 1px);"
>
  {#each [...Array(cm).keys()] as c}
    <div class="cm" style="height: {1000 / len}%; top:{(1000 * c) / len}%;">
      <div class="text">{c}</div>
      <div>
        {#each [...Array(10).keys()] as m}
          <div class="mm " style="height: 10%; top:{10 * m}%;" />
        {/each}
      </div>
    </div>
  {/each}

  <div class="cm" style="height: {1000 / len}%; top:{(1000 * cm) / len}%;">
    <div class="text">{cm}</div>
    <div>
      {#each [...Array(mm + 1).keys()] as m}
        <div class="mm " style="height: 10%; top:{10 * m}%;" />
      {/each}
    </div>
  </div>
</div>

<style lang="postcss">
  * {
    @apply opacity-90;
  }

  .cm {
    @apply text-right absolute font-mono h-4;
    transform: translateY(-0.25rem);
  }

  .mm {
    @apply absolute border-b border-gray-600;
    width: 0.25rem;
  }

  .text {
    transform: translateX(0.625rem) translateY(-0.4rem);
  }

  .mm:first-of-type {
    width: 1rem;
    transform: translateX(-0.75rem);
  }

  .mm:nth-of-type(6n) {
    width: 0.5rem;
    transform: translateX(-0.25rem);
  }
</style>
