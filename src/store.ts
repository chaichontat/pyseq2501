import { browser } from "$app/env";
import type { Writable } from "svelte/store";
import { writable } from "svelte/store";
import type { Cmds, Reagent } from "./cmds";
import { defaults, reagentDefault } from "./cmds";
import websocketStore from "./ws_store";


export type XY = {
  x: number;
  y: number;
}

export type Status = {
  x: number;
  y: number;
  z_tilt: [number, number, number];
  z_obj: number;
  laser_r: number;
  laser_g: number;
  shutter: boolean;
  moving: boolean;
  msg: string;
};

let status: Status = {
  x: -1,
  y: -1,
  z_tilt: [-1, -1, -1],
  z_obj: -1,
  laser_r: -1,
  laser_g: -1,
  shutter: false,
  moving: false,
  msg: "",
};

export type Recipe = {
  reagents: NReagent[],
  cmds: NCmd[],
  max_uid: number
}

export type UserSettings = {
  n: number;
  x: number
  y: number
  z_tilt: number | [number, number, number],
  z_obj: number,
  laser_r: number,
  laser_g: number,
  flowcell: boolean,
  mode: "manual" | "automatic" | "editingA" | "editingB",
  recipes: [Recipe | null, Recipe | null]
}

export type NReagent = { uid: number; reagent: Reagent };
export type NCmd = { uid: number; cmd: Cmds };

export type Hist = {
  counts: number[],
  bin_edges: number[]
}

export type Img = {
  img: string,
  n: number,
  hist: Hist
}

export const recipeDefault: Recipe = {
  reagents: [{ uid: 0, reagent: { ...reagentDefault } }], cmds: [{ uid: 0, cmd: { ...defaults.image } }], max_uid: 2
}

const userDefault: UserSettings = {
  n: 16, x: 0, y: 0, z_tilt: 19850, z_obj: 32000, laser_r: 5, laser_g: 5, flowcell: false,
  mode: "automatic", recipes: [{ ...recipeDefault }, { ...recipeDefault }]
}

let img: Img = { n: 0, img: "", hist: { counts: [10], bin_edges: [0] } }

export const imgStore = (browser)
  ? websocketStore(`ws://${ window.location.hostname }:8000/img`, img, (x) => JSON.parse(JSON.parse(x)))
  : writable(img)

export const statusStore: Writable<Status> = (browser)
  ? websocketStore(`ws://${ window.location.hostname }:8000/status`, status, (x): Status => JSON.parse(JSON.parse(x)))
  : writable(status)

export const userStore: Writable<UserSettings> = (browser)
  ? websocketStore(`ws://${ window.location.hostname }:8000/user`, userDefault, (x): Status => JSON.parse(JSON.parse(x)))
  : writable(userDefault)

export const cmdStore: Writable<undefined> = (browser)
  ? websocketStore(`ws://${ window.location.hostname }:8000/cmd`, undefined, (x): Status => JSON.parse(JSON.parse(x)))
  : writable(undefined)

// export let status: Status = {
//   x: 2,
//   y: 5,
//   z_tilt: [0, 1, 2],
//   z_obj: 4,
//   laser_r: 3,
//   laser_g: 5,
//   shutter: false,
// };

// function genSSE(): EventSource {
//   const sse = new EventSource(`http://${ window.location.hostname }:8000/status`);
//   sse.onopen = () => (connected = true);
//   sse.onmessage = (event: MessageEvent<string>) => (status = JSON.parse(event.data));
//   sse.onerror = () => {
//     sse.close()
//     connected = false
//     console.log("Reconnecting SSE")
//     setTimeout(genSSE, 2000)
//   }
//   return sse;
// }

// if (typeof window !== 'undefined') {
//   genSSE()
// }

