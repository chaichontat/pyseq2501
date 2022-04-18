<script lang="ts">
  export let name_: string;
  export let color: string;
  export let userPower: number;
  export let power: number;

  function update() {
    // Update only when focus lost.
    userPower = pow;
  }

  let pow = userPower;
  $: pow = userPower;
</script>

<tr class="align-middle" style="--this-color: {color}">
  <th>
    <svg class="inline-block h-4 w-4 -translate-y-0.5" viewBox="0 0 20 20" fill={color}>
      <path
        fill-rule="evenodd"
        d="M12.395 2.553a1 1 0 00-1.45-.385c-.345.23-.614.558-.822.88-.214.33-.403.713-.57 1.116-.334.804-.614 1.768-.84 2.734a31.365 31.365 0 00-.613 3.58 2.64 2.64 0 01-.945-1.067c-.328-.68-.398-1.534-.398-2.654A1 1 0 005.05 6.05 6.981 6.981 0 003 11a7 7 0 1011.95-4.95c-.592-.591-.98-.985-1.348-1.467-.363-.476-.724-1.063-1.207-2.03zM12.12 15.12A3 3 0 017 13s.879.5 2.5.5c0-1 .5-4 1.25-4.5.5 1 .786 1.293 1.371 1.879A2.99 2.99 0 0113 13a2.99 2.99 0 01-.879 2.121z"
        clip-rule="evenodd"
      />
    </svg>
    {name_}
  </th>

  <td class="h-10 text-center align-middle font-bold text-gray-600" on:blur={update}>{pow}</td>
  <td class="text-center font-mono text-lg font-bold text-gray-800">{power}</td>
  <td class="text-right">mW</td>
</tr>

<style lang="postcss">
  input {
    text-align: center;
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
    transform: translateX(-1.2em) translateY(0.4em);
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
    @apply p-1 transition-all;
  }
</style>
