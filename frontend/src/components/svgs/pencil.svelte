<script lang="ts">
  let cl = "";
  export { cl as class };
  let modifying: boolean = false;
</script>

<slot name="before" {modifying} />
<button
  class={cl}
  on:click={() => {
    modifying = true;
    console.log(modifying);
  }}
>
  <svg
    xmlns="http://www.w3.org/2000/svg"
    class="h-4 w-4 fill-gray-700 hover:fill-blue-800 transition-colors"
    viewBox="0 0 20 20"
  >
    <path d="M17.414 2.586a2 2 0 00-2.828 0L7 10.172V13h2.828l7.586-7.586a2 2 0 000-2.828z" />
    <path
      fill-rule="evenodd"
      d="M2 6a2 2 0 012-2h4a1 1 0 010 2H4v10h10v-4a1 1 0 112 0v4a2 2 0 01-2 2H4a2 2 0 01-2-2V6z"
      clip-rule="evenodd"
    />
  </svg>
</button>
<slot name="after" {modifying} />
