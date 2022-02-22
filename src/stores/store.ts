
import { browser } from "$app/env";
import type { Writable } from "svelte/store";
import { writable } from "svelte/store";
import { cmdDefaults, TakeImage } from "./command";
import { experimentDefault, NExperiment } from "./experiment";
import { Img, imgDefault } from "./imaging";
import { Status, statusDefault } from "./status";
import websocketStore from "./ws_store";


let try_connect: boolean = true;  // Check if in GitHub Actions.

export type XY = {
  x: number;
  y: number;
};

export type UserSettings = {
  block: Block;
  max_uid: number;
  mode: "manual" | "automatic" | "editingA" | "editingB";
  exps: [NExperiment, NExperiment];
  image_params: TakeImage & { fc: boolean };
};

export type Block = "" | "moving" | "ejecting" | "capturing" | "previewing" | "all";

const userDefault: Readonly<UserSettings> = {
  block: "",
  max_uid: 2,
  mode: "editingA",
  exps: [{ ...experimentDefault }, { ...experimentDefault }],
  image_params: { ...cmdDefaults["takeimage"], fc: false },
};

export type CmdReturns = { step?: [number, number, number]; msg?: string, error?: string };

export const imgStore: Writable<Img> = writable({ ...imgDefault });

// TODO: Make this read-only.
export const statusStore: Writable<Status> =
  try_connect && browser ? websocketStore(`ws://${ window.location.hostname }:8000/status`, { ...statusDefault }, (x): Status => JSON.parse(x)) : writable({ ...statusDefault });

export const userStore: Writable<UserSettings> =
  try_connect && browser ? websocketStore(`ws://${ window.location.hostname }:8000/user`, { ...userDefault }, (x) => JSON.parse(x)) : writable({ ...userDefault });

export const cmdStore: Writable<CmdReturns> =
  try_connect && browser ? websocketStore(`ws://${ window.location.hostname }:8000/cmd`, { msg: "ok" }, (x) => JSON.parse(x), false) : writable({ msg: "ok" });

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

