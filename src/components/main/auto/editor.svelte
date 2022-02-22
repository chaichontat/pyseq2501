<script lang="ts">
  import { browser } from "$app/env";
  import Reagents from "$comps/main/auto/reagents/reagents.svelte";
  import Steps from "$comps/main/auto/steps/steps.svelte";
  import { Experiment, experimentDefault, fromExperiment, NExperiment, toExperiment } from "$src/stores/experiment";
  import rawExperimentSchema from "$src/stores/experiment_schema.json";
  import { userStore as us } from "$src/stores/store";
  import { Menu, MenuButton, MenuItem, MenuItems } from "@rgossiaux/svelte-headlessui";
  import Ajv from "ajv";
  import yaml from "js-yaml";
  import { cubicInOut } from "svelte/easing";
  import { fade } from "svelte/transition";
  import type { Event } from "ws";
  import ProgressManual from "../manual/progress_manual.svelte";

  // let files: FileList;
  export let fc: 0 | 1;

  const ajv = new Ajv();
  const validate = ajv.compile(rawExperimentSchema);
  let stats = { height: 0, width: 0, n_cols: 0, n_bundles: 0, n_z: 1, time: 0 };
  // async function uploadFile() {
  //   const file = files.item(0);
  //   if (browser && file) {
  //     const formData = new FormData();
  //     formData.append("file", file, file.name);
  //     console.log(formData);
  //     const resp = await fetch(`http://${window.location.hostname}:8000/experiment/${fc}`, { method: "POST", body: formData });
  //     if (!resp.ok) {
  //       console.error((await resp.json()).detail);
  //     }
  //   }
  // }

  function toYAML(ne: NExperiment) {
    const blob = new Blob([yaml.dump(toExperiment(ne))], { type: "application/yaml" });
    const elem = window.document.createElement("a");
    elem.href = window.URL.createObjectURL(blob);
    elem.download = `${ne.name}.yaml`;
    document.body.appendChild(elem);
    elem.click();
    document.body.removeChild(elem);
  }

  async function fromYAML(e: { currentTarget: EventTarget & HTMLInputElement }) {
    if (!e.currentTarget.files) return;
    const raw = await e.currentTarget.files[0].text();
    try {
      const parsed = yaml.load(raw) as Experiment;
      if (!validate(parsed)) {
        alert("Invalid file!");
        return;
      }

      const ne = fromExperiment(parsed, $us.max_uid);
      $us.max_uid += ne.reagents.length + ne.cmds.length;
      $us.exps[fc] = ne;
    } catch (e) {
      alert(e);
    }
  }
</script>

<div class="flex items-center">
  <span>
    <!-- Back -->
    <button on:click={() => ($us.mode = "automatic")}>
      <svg xmlns="http://www.w3.org/2000/svg" class="w-7 h-7 mr-1 translate-y-0.5 stroke-gray-700 hover:stroke-gray-800 active:stroke-black" fill="none" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
      </svg>
    </button>
    <p class="inline-block my-8 ml-2 text-4xl font-extrabold tracking-tight text-gray-700 dark:text-white">Flowcell {fc ? "B" : "A"}</p>
  </span>

  <!-- Download -->
  <!-- REMOVE BEFORE FLIGHT -->
  <div class="flex gap-x-2">
    <button class="px-4 py-1 ml-8 text-base font-medium rounded-lg h-11 white-button" on:click={() => toYAML($us.exps[fc])}>
      <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
      </svg>
      Download
    </button>

    <!-- <form action={`http://localhost:8000/experiment/${fc}/`} enctype="multipart/form-data" method="post" bind:this={form}> -->
    <label>
      <input class="hidden" name="file" type="file" accept=".yaml, .yml" on:change={fromYAML} />
      <div class="px-4 py-1 text-base font-medium rounded-lg cursor-pointer h-11 white-button">
        <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
        </svg>
        Upload
      </div>
    </label>
    <!-- </form> -->
    <!-- <form action={`http://localhost:8000/uploadfiles/`} enctype="multipart/form-data" method="post" bind:this={form}>
      <input class="" type="file" accept=".yaml, .yml" />
      <div class="px-4 py-1 text-base font-medium rounded-lg cursor-pointer h-11 white-button">
        <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
        </svg>
        Upload
      </div>
      <input type="submit" />
    </form> -->

    <Menu class="relative inline-block ">
      <MenuButton class="inline-flex justify-center w-full px-2 py-1 font-medium rounded-lg h-11 white-button">
        <!-- Plus -->
        <svg aria-hidden="true" class="w-5 h-5 ml-1 text-gray-600 " viewBox="0 0 16 16" fill="currentColor" style="display: inline-block; vertical-align: text-bottom; overflow: visible">
          <path fill-rule="evenodd" d="M7.75 2a.75.75 0 01.75.75V7h4.25a.75.75 0 110 1.5H8.5v4.25a.75.75 0 11-1.5 0V8.5H2.75a.75.75 0 010-1.5H7V2.75A.75.75 0 017.75 2z" />
        </svg>
        <!-- Chevron down -->
        <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 ml-2 -mr-1 text-gray-800" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
        </svg>
      </MenuButton>

      <MenuItems class="absolute right-0 z-10 mt-2 space-y-1 overflow-hidden origin-top-right bg-white border divide-gray-100 rounded-md shadow w-36 focus:outline-none">
        <div transition:fade={{ duration: 100, easing: cubicInOut }}>
          <!-- New -->
          <MenuItem let:active
            ><div class:bg-blue-700={active} class:text-white={active} class="z-0 w-full px-2 py-2 pl-4" on:click={() => ($us.exps[fc] = { ...experimentDefault })}>New</div></MenuItem
          >
        </div>
      </MenuItems>
    </Menu>
  </div>
</div>

<ProgressManual bind:stats />
<!-- <ProgressAuto fc={fc} /> -->

<!-- {#if $us.exps[fc]} -->

<!-- Name, Image Path -->
<!-- <ProgressManual /> -->
<p class="pb-3 mt-8 text-2xl font-bold text-gray-800 border-b">Details</p>
<div class="flex flex-col text-lg font-medium">
  <p class="text-lg">Name</p>
  <input type="text" class="max-w-md mt-1 mb-4 pretty" bind:value={$us.exps[fc].name} class:invalid={!$us.exps[fc].name} />
  <!-- FileSystemAccessAPI cannot give path upstream of what user chooses. -->
  <p class="text-lg">Image Path</p>
  <input type="text" class="max-w-md mt-1 mb-4 pretty" bind:value={$us.exps[fc].path} class:invalid={!$us.exps[fc].path} />
</div>

<Reagents {fc} />
<Steps {fc} />
<p class="mt-6 mb-1 text-2xl font-bold text-gray-800">Preview</p>
<!-- <Preview /> -->

<!-- Editor -->
<!-- {:else} -->
<!-- New or Upload -->
<!-- <div class="flex items-center justify-center w-full h-[50vh]">
    <div class="inline-flex text-2xl rounded-md shadow-sm" role="group">
      <button type="button" class="px-8 py-6 font-medium rounded-l-lg white-button" on:click={() => ($us.exps[fc] = { ...recipeDefault })}>
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
        </svg>
        New Experiment
      </button>

      <button type="button" class="px-8 py-6 font-medium border-l-0 rounded-r-lg white-button ">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
        </svg>
        Upload
      </button>
    </div>
  </div> -->

<!-- {/if} -->
<style lang="postcss">
  svg {
    @apply mr-1;
  }
</style>
