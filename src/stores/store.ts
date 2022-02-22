
import { browser } from "$app/env";
import type { Writable } from "svelte/store";
import { writable } from "svelte/store";
import { cmdDefaults, TakeImage } from "./command";
import { experimentDefault, NExperiment } from "./experiment";
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

export type CommandResponse = { step?: [number, number, number]; msg?: string, error?: string };



// TODO: Make this read-only.
export const statusStore: Writable<Status> =
  try_connect && browser ? websocketStore(`ws://${ window.location.hostname }:8000/status`, { ...statusDefault }, (x): Status => JSON.parse(x)) : writable({ ...statusDefault });

export const userStore: Writable<UserSettings> = writable({ ...userDefault })

export const user_ws = try_connect && browser ? websocketStore(`ws://${ window.location.hostname }:8000/user`, { ...userDefault }, (x) => JSON.parse(x)) : writable({ ...userDefault });

export const cmdStore: Writable<CommandResponse> =
  try_connect && browser ? websocketStore(`ws://${ window.location.hostname }:8000/cmd`, { msg: "ok" }, (x) => JSON.parse(x), false) : writable({ msg: "ok" });



export async function initial_get() {
  if (browser) {
    try {
      const raw = await fetch(`http://${ window.location.hostname }:8000/usersettings`)
      const us = await raw.json() as UserSettings
      userStore.set(us)
    } catch (e) {
      setTimeout(initial_get, 1000);
      console.error("Cannot get initial user settings.")
    }
  }
}

function updateUserSettings() {
  let t0 = Date.now();
  let timeout = setTimeout(() => undefined, 1000);

  userStore.subscribe((us) => {
    let t = Date.now();
    const f = () => {
      user_ws.set(us);
      t0 = Date.now();
    }

    if (t - t0 < 1000) {
      clearTimeout(timeout);
      timeout = setTimeout(f, 1000 - (t - t0));
    } else {
      f()
    }
  });
}

updateUserSettings();


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

