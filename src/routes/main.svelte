<script lang="ts">
  import Preview from "$comps/main/preview.svelte";
  import Progress from "$comps/main/progress.svelte";
  import Steps from "$src/components/main/steps/steps.svelte";
</script>

<svelte:head>
  <title>PySeq 2501</title>
</svelte:head>
<!-- <script>
  import Graph from "./graph.svelte";
</script> -->

<Progress />

<Steps />
<!-- <Graph /> -->
<Preview />
