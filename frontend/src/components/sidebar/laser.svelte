<script lang="ts">
  export let desc;
  export let color;
</script>

<li>
  <span>
    <div class="w-24">{desc}</div>
    <input
      type="range"
      min="1"
      max="400"
      value="60"
      class="tooltip range range-md pl-"
      data-tip="hello"
      style={"--range-shdw:" + color}
    />
  </span>
</li>
