<script lang="ts">
  import Reagents from "$comps/main/auto/reagents/reagents.svelte";
  import Steps from "$comps/main/auto/steps/steps.svelte";
  import type { Experiment, NExperiment } from "$src/stores/experiment";
  import { fromExperiment, genExperimentDefault, toExperiment } from "$src/stores/experiment";
  import rawExperimentSchema from "$src/stores/experiment_schema.json";
  import { localStore as ls, userStore as us } from "$src/stores/store";
  import { Menu, MenuButton, MenuItem, MenuItems } from "@rgossiaux/svelte-headlessui";
  import Ajv from "ajv";
  import yaml from "js-yaml";
  import { cubicInOut } from "svelte/easing";
  import { fade } from "svelte/transition";
  import ProgressAuto from "./progress_auto.svelte";

  export let fc_: 0 | 1 = 0;

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
    const blob = new Blob([yaml.dump(toExperiment(ne), { noRefs: true })], { type: "application/yaml" });
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
      $us.exps[fc_] = ne;
    } catch (e) {
      alert(e);
    }
  }
</script>

<div class="relative flex items-center">
  <div class="absolute right-60 -top-20 -z-10 text-[500px] font-semibold text-indigo-700 opacity-10" class:text-fuchsia-700={fc_}>
    {{ 0: "A", 1: "B" }[fc_]}
  </div>
  <span>
    <!-- Back -->
    <button on:click={() => ($ls.mode = "automatic")}>
      <svg xmlns="http://www.w3.org/2000/svg" class="mr-1 h-7 w-7 translate-y-0.5 stroke-gray-700 hover:stroke-gray-800 active:stroke-black" fill="none" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
      </svg>
    </button>
    <p class="my-8 ml-2 inline-block text-4xl font-extrabold tracking-tight text-gray-700">Flowcell {{ 0: "A", 1: "B" }[fc_]}</p>
  </span>

  <!-- Download -->
  <div class="flex gap-x-2">
    <button class="white-button ml-8 h-11 rounded-lg px-4 py-1 text-base font-medium" on:click={() => toYAML($us.exps[fc_])}>
      <svg xmlns="http://www.w3.org/2000/svg" class="mr-1 h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
      </svg>
      Download
    </button>

    <!-- <form action={`http://localhost:8000/experiment/${fc}/`} enctype="multipart/form-data" method="post" bind:this={form}> -->
    <label>
      <input class="hidden" name="file" type="file" accept=".yaml, .yml" on:change={fromYAML} />
      <div class="white-button h-11 cursor-pointer rounded-lg px-4 py-1 text-base font-medium">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
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
      <MenuButton class="white-button inline-flex h-11 w-full justify-center rounded-lg px-2 py-1 font-medium">
        <!-- Plus -->
        <svg aria-hidden="true" class="ml-1 h-5 w-5 text-gray-600 " viewBox="0 0 16 16" fill="currentColor" style="display: inline-block; vertical-align: text-bottom; overflow: visible">
          <path fill-rule="evenodd" d="M7.75 2a.75.75 0 01.75.75V7h4.25a.75.75 0 110 1.5H8.5v4.25a.75.75 0 11-1.5 0V8.5H2.75a.75.75 0 010-1.5H7V2.75A.75.75 0 017.75 2z" />
        </svg>
        <!-- Chevron down -->
        <svg xmlns="http://www.w3.org/2000/svg" class="ml-2 -mr-1 h-5 w-5 text-gray-800" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
        </svg>
      </MenuButton>

      <MenuItems class="absolute right-0 z-10 mt-2 w-36 origin-top-right space-y-1 divide-gray-100 overflow-hidden rounded-md border bg-white shadow focus:outline-none">
        <div transition:fade={{ duration: 100, easing: cubicInOut }}>
          <!-- New -->
          <MenuItem let:active
            ><div
              class:bg-blue-700={active}
              class:text-white={active}
              class="z-0 my-1 w-full px-2 py-2 pl-4"
              on:click={() => {
                $us.exps[fc_] = genExperimentDefault($us.max_uid);
                $us.max_uid += 3;
              }}
            >
              New
            </div></MenuItem
          >
        </div>
      </MenuItems>
    </Menu>
  </div>
</div>

<div class="flex flex-col">
  <div>
    <ProgressAuto {fc_} />
  </div>
  <div>
    <p class="mt-8 border-b border-gray-300 pb-3 text-2xl font-bold text-gray-800">Details</p>
    <div class="flex flex-col text-lg font-medium">
      <p class="pt-3 text-lg">Name</p>
      <input type="text" class="pretty mt-1 mb-4 max-w-md" bind:value={$us.exps[fc_].name} class:invalid={!$us.exps[fc_].name} />
      <!-- FileSystemAccessAPI cannot give path upstream of what user chooses. -->
      <p class="text-lg">Image Path</p>
      <input type="text" class="pretty mt-1 mb-4 max-w-md" bind:value={$us.exps[fc_].path} class:invalid={!$us.exps[fc_].path} />
    </div>
  </div>
</div>

<Reagents {fc_} />
<Steps {fc_} />

<style lang="postcss">
  svg {
    @apply mr-1;
  }
</style>
