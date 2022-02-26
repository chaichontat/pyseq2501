
import { browser } from "$app/env";
import type { Readable, Writable } from "svelte/store";
import { writable } from "svelte/store";
import { cmdDefaults, TakeImage } from "./command";
import { experimentDefault, NExperiment } from "./experiment";
import { Status, statusDefault } from "./status";
import writableWebSocket, { readableWebSocket } from "./ws_store";


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

export type LocalInfo = { "mode": "auto" | "editingA" | "editingB" | "manual", "connected": boolean }
export const localStore: Writable<LocalInfo> = writable({ mode: "auto", connected: false })

// TODO: Make this read-only.
export const statusStore: Readable<Status> =
  try_connect && browser ? readableWebSocket(`ws://${ window.location.hostname }:8000/status`, { ...statusDefault }, { localStore })
    : writable({ ...statusDefault });

export const userStore: Writable<UserSettings> = writable({ ...userDefault })

const user_ws: Writable<UserSettings> = try_connect && browser ? writableWebSocket(`ws://${ window.location.hostname }:8000/user`, { ...userDefault },
  { beforeOpen: initial_get })
  : writable({ ...userDefault });

export const cmdStore: Writable<CommandResponse> =
  try_connect && browser ? writableWebSocket(`ws://${ window.location.hostname }:8000/cmd`, { msg: "ok" }, { broadcastOnSet: false })
    : writable({ msg: "ok" });


export async function initial_get() {
  if (browser) {
    while (true) {
      try {
        const raw = await fetch(`http://${ window.location.hostname }:8000/usersettings`)
        const us = await raw.json() as UserSettings
        userStore.set(us)
        return;
      } catch (e) {
        console.error("Cannot get initial user settings.")
        // await new Promise(r => setTimeout(r, 1000));  // Sleep for 1 second.
      }
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

