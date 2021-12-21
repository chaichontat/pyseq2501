<script lang="ts">
  export let name;
  export let color;
</script>

<tr class="text-base" style="--this-color: {color}">
  <th><span class="dot font-semibold">{name}</span></th>

  <td>
    <input
      type="number"
      min="0"
      max="1000"
      step="1"
      class="text-base input input-bordered pr-2 w-10/12 float-right"
      style="height:2em;"
    />
  </td>
  <td class="text-center font-bold font-mono">45</td>
  <td class="text-right">mW</td>
</tr>

<style lang="postcss">
  input {
    text-align: right;
  }

  input:focus {
    outline: 2px solid transparent;
    outline-offset: 2px;
    box-shadow: 0 0 0 2px hsl(var(--b1)), 0 0 0 4px hsla(var(--bc) / 0.2);
  }

  /* Remove arrows */
  input::-webkit-outer-spin-button,
  input::-webkit-inner-spin-button {
    -webkit-appearance: none;
    margin: 0;
  }
  input[type="number"] {
    -moz-appearance: textfield;
  }

  input:invalid {
    @apply border-red-600;
    text-decoration: line-through;
  }

  input:valid {
    @apply border-gray-400;
    text-decoration: none;
  }

  .dot::before {
    content: "";
    clip-path: circle();
    transform: translateX(-1.2em) translateY(0.33em);
    position: absolute;
    width: 0.75em;
    height: 0.75em;
    background: var(--this-color);
  }
  .dot {
    margin-left: 1em;
  }

  th,
  td {
    @apply transition-all p-1;
  }
</style>
