import { onMount } from "svelte";
import { writable } from "svelte/store";
import type { Writable } from "svelte/store";
import websocketStore from "./store";

export let store: null | Writable<string | null> = null

// onMount(() => {
//     store = websocketStore(`ws://${ window.location.hostname }:8000/img`);
// })
