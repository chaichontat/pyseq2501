import type { Writable } from "svelte/store";
import { writable } from "svelte/store";
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

export type UserSettings = {
  n: number;
  x: number
  y: number
  z_tilt: number | [number, number, number],
  z_obj: number,
  laser_r: number,
  laser_g: number,
  flowcell: boolean,
}

let userDefault: UserSettings = { n: 8, x: 0, y: 0, z_tilt: 19850, z_obj: 32000, laser_r: 5, laser_g: 5, flowcell: false }

let img = { n: 0, img: "" }

export const mainStore = (!import.meta.env.SSR)
  ? websocketStore(`ws://${ window.location.hostname }:8000/img`, img, (x) => JSON.parse(JSON.parse(x)))
  : writable(img)

export const statusStore: Writable<Status> = (!import.meta.env.SSR)
  ? websocketStore(`ws://${ window.location.hostname }:8000/status`, status, (x): Status => JSON.parse(JSON.parse(x)))
  : writable(status)

export const userStore: Writable<UserSettings> = (!import.meta.env.SSR)
  ? websocketStore(`ws://${ window.location.hostname }:8000/user`, userDefault, (x): Status => JSON.parse(JSON.parse(x)))
  : writable(userDefault)

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

