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
  msg: string;
};

let status: Status = {
  x: 2,
  y: 5,
  z_tilt: [0, 1, 2],
  z_obj: 4,
  laser_r: 3,
  laser_g: 5,
  shutter: false,
  msg: "",
};

export type UserSettings = {
  n: number;
}

export const mainStore = (typeof window !== 'undefined')
  ? websocketStore(`ws://${ window.location.hostname }:8000/img`)
  : writable(undefined)

export const statusStore: Writable<Status> = (typeof window !== 'undefined')
  ? websocketStore(`ws://${ window.location.hostname }:8000/status`, status, (x): Status => JSON.parse(JSON.parse(x)))
  : writable(status)

export const userStore: Writable<UserSettings> = writable({ n: 5 })

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

