<script lang="ts">
  import { config } from "$src/stores/store";
  let is2500 = false;

  (async () => {
    if ((await config).machine === "HiSeq2500") is2500 = true;
  })();
</script>

<div class="z-50 mx-auto space-x-1 navbar max-w-none">
  <div class="flex items-center flex-none">
    <span aria-label="Homepage" class="px-2 flex-0 md:px-4 ">
      <div class="inline-block text-3xl">
        <span class="font-light normal-case">PySeq</span>
        <span class="font-semibold grad" class:grad2500={is2500}>{is2500 ? 2501 : 2001}</span>
      </div>
    </span>
  </div>
  <a href="https://github.com/chaichontat/pyseq2501/" target="_blank" rel="nofollow" class="font-mono text-xs opacity-50">
    <div data-tip="Changelog" class="tooltip tooltip-bottom">
      <span class="hidden lg:inline">version</span>
      &nbsp;0.0.1
    </div>
  </a>
</div>

<style lang="postcss">
  .grad {
    background: linear-gradient(61.68deg, #225de6 -4.27%, #a664fd 116.09%);
    background-clip: text;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }

  .grad2500 {
    background: linear-gradient(61.68deg, #eea4bc, #be88c4, #9186e7);
    background-clip: text;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }
</style>
