<script lang="ts">
  import Preview from "./preview.svelte";
  import Progress from "./progress.svelte";
</script>

<svelte:head>
  <title>PySeq 2501</title>
</svelte:head>
<!-- <script>
  import Graph from "./graph.svelte";
</script> -->

<Progress curr={null} full={null} />
<!-- <Graph /> -->
<Preview />
