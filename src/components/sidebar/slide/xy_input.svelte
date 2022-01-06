<script lang="ts">
  import type { XY } from "src/store";
  export let xy: XY = { x: 0, y: 0 };
  export let xy_user: XY = { x: 0, y: 0 };
</script>

<!-- XY Input -->

<div class="form-control self-center mt-4">
  <label class="font-medium input-group">
    <span
      ><div data-tip={xy.x.toFixed(2)} class="tooltip tooltip-bottom">
        <b>X</b>
      </div></span
    >
    <input
      bind:value={xy_user.x}
      type="number"
      min="-5"
      max="30"
      step="0.7"
      class="text-lg text-center input input-bordered inputcheck w-28 h-10"
    />
    <span
      ><div data-tip={xy.y.toFixed(2)} class="tooltip tooltip-bottom">
        <b>Y</b>
      </div></span
    >
    <input
      bind:value={xy_user.y}
      type="number"
      min="-5"
      max="80"
      step="0.7"
      class="text-lg text-center input input-bordered inputcheck w-28 h-10"
    />

    <button
      class="font-sans content-center w-12 text-indigo-100 transition-colors duration-150 bg-indigo-700 rounded-lg focus:shadow-outline hover:bg-indigo-800"
      tabindex="0"
      >Go
    </button>
  </label>
</div>
