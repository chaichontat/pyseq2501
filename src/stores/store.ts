import { browser } from "$app/env";
import type { Writable } from "svelte/store";
import { writable } from "svelte/store";
import type { TakeImage } from "./command";
import { cmdDefaults } from "./command";
import type { NExperiment } from "./experiment";
import { genExperimentDefault } from "./experiment";
import type { AFImg, Img } from "./imaging";
import { imgDefault } from "./imaging";
import type { Status } from "./status";
import { statusDefault } from "./status";
import type { AsymWritable } from "./ws_store";
import writableWebSocket, { asymWritableWebSocket } from "./ws_store";

export type XY = {
  x: number;
  y: number;
};

export type UserSettings = {
  block: Block;
  max_uid: number;
  exps: [NExperiment, NExperiment];
  image_params: TakeImage & { fc: boolean };
};

export type Block = "" | "moving" | "ejecting" | "capturing" | "previewing" | "all";

const userDefault: Readonly<UserSettings> = {
  block: "",
  max_uid: 6,
  exps: [genExperimentDefault(0), genExperimentDefault(3)],
  image_params: { ...cmdDefaults["takeimage"], fc: false },
};

export type FCCmd = {
  fc: boolean;
  cmd: "start" | "validate" | "stop";
};

export type LocalInfo = { mode: "automatic" | "editingA" | "editingB" | "manual"; connected: boolean; img: Img; afimg: AFImg };
export const localStore: Writable<LocalInfo> = writable({
  mode: "automatic",
  connected: false,
  img: { ...imgDefault },
  afimg: { afimg: Array(259).fill(""), laplacian: Array(259).fill(0) },
});

export const statusStore: Writable<Status> = browser
  ? writableWebSocket(`ws://${window.location.hostname}:8000/status`, { ...statusDefault }, { localStore, onOpen: firstLoad, sendOnSet: false })
  : writable({ ...statusDefault });

export const userStore: Writable<UserSettings> = writable({ ...userDefault });

const user_ws: Writable<UserSettings> = browser
  ? writableWebSocket(`ws://${window.location.hostname}:8000/user`, { ...userDefault }, { onOpen: initial_get })
  : writable({ ...userDefault });

export type MoveManual = {
  xy0: [number?, number?];
  xy1: [number?, number?];
  z_tilt: number | [number?, number?, number?];
  laser_onoff: [boolean?, boolean?];
  lasers: [number?, number?];
  z_obj: number;
  z_spacing: number;
  od: [number?, number?];
};

export type CommandResponse = { step?: [number, number, number]; msg?: string; error?: string };
export type CommandWeb = { move?: Partial<MoveManual>; cmd?: "preview0" | "preview1" | "capture" | "stop" | "autofocus"; fccmd?: FCCmd };
export const cmdStore: AsymWritable<Partial<CommandResponse>, Partial<CommandWeb>> = asymWritableWebSocket(
  `ws://${browser ? window.location.hostname : ""}:8000/cmd`,
  { msg: "ok" },
  { cmd: "stop" }
);

export async function initial_get() {
  if (browser) {
    for (;;) {
      try {
        const raw = await fetch(`http://${window.location.hostname}:8000/usersettings`);
        const us = (await raw.json()) as UserSettings;
        userStore.set(us);
        return;
      } catch (e) {
        console.error("Cannot get initial user settings.");
        // await new Promise(r => setTimeout(r, 1000));  // Sleep for 1 second.
      }
    }
  }
}

function updateUserSettings() {
  let t0 = Date.now();
  let timeout = setTimeout(() => undefined, 1000);

  userStore.subscribe((us) => {
    const t = Date.now();
    const f = () => {
      user_ws.set(us);
      t0 = Date.now();
    };

    if (t - t0 < 1000) {
      clearTimeout(timeout);
      timeout = setTimeout(f, 1000 - (t - t0));
    } else {
      f();
    }
  });
}

updateUserSettings();

function updateImg(c: CommandResponse) {
  if (browser) {
    if (c.msg === "imgReady") {
      fetch(`http://${window.location.hostname}:8000/img`)
        .then((response: Response) => response.json())
        .then((img: Img) => localStore.update((l) => ({ ...l, img })))
        .catch((e) => alert(e));
      userStore.update((u) => ({ ...u, block: "" }));
    } else if (c.msg === "afimgReady") {
      fetch(`http://${window.location.hostname}:8000/afimg`)
        .then((response: Response) => response.json())
        .then((afimg: AFImg) => localStore.update((l) => ({ ...l, afimg })))
        .catch((e) => alert(e));
      userStore.update((u) => ({ ...u, block: "" }));
    } else if (c.msg === "moveDone") {
      userStore.update((u) => ({ ...u, block: "" }));
    }
  }
}

cmdStore.subscribe(updateImg);

async function firstLoad() {
  await fetch(`http://${window.location.hostname}:8000/img`)
    .then((response: Response) => response.json())
    .then((img: Img) => localStore.update((l) => ({ ...l, img })))
    .catch(() => undefined);

  await fetch(`http://${window.location.hostname}:8000/afimg`)
    .then((response: Response) => response.json())
    .then((afimg: AFImg) => localStore.update((l) => ({ ...l, afimg })))
    .catch(() => undefined);
}

if (browser) firstLoad().catch(() => undefined);

export type Config = {
  machine: "HiSeq2000" | "HiSeq2500";
  logPath: string;
  logLevel: "DEBUG" | "INFO" | "WARNING" | "ERROR" | "CRITICAL";
};

export const config: Promise<Readonly<Config>> = browser
  ? fetch(`http://${window.location.hostname}:8000/config`).then((response: Response): Promise<Config> => response.json())
  : new Promise(() => ({ machine: "HiSeq2000", logPath: "", logLevel: "DEBUG" }));
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
