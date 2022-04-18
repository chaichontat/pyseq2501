import { browser } from "$app/env";
import type { Readable, Writable } from "svelte/store";
import { writable } from "svelte/store";
import type { LocalInfo } from "./store";

type ValidType = string; // | ArrayBufferLike | Blob | ArrayBufferView;

type Sendable = object | string | number | Array<object> | Array<string> | Array<number>;

export type wsConfig<T extends Sendable | Set<Sendable>> = {
  f?: (x: ValidType) => T;
  onOpen?: () => Promise<void>;
  localStore?: Writable<LocalInfo>;
  sendOnSet?: boolean;
};

export function writableWebSocket<T extends Sendable | Set<Sendable>>(
  url: string,
  initialValue: T,
  { f = JSON.parse, onOpen, localStore, sendOnSet = true }: wsConfig<T> = {}
): Writable<T> {
  let socket: WebSocket;
  let timeout: ReturnType<typeof setTimeout> | null;
  const { set: setStore, subscribe, update } = writable(initialValue);

  function _open() {
    console.log("Connecting");
    timeout = null;

    socket = new WebSocket(url);
    socket.onmessage = (event: MessageEvent): void => setStore(f(event.data as string));

    socket.onopen = async () => {
      if (onOpen) await onOpen();
      if (localStore) localStore.update((curr) => ({ ...curr, connected: true }));
      if (timeout) {
        clearTimeout(timeout);
        timeout = null;
      }
    };

    socket.onclose = () => {
      if (localStore) localStore.update((curr) => ({ ...curr, connected: false }));
      if (!timeout) timeout = setTimeout(_open, 2000);
      console.error("Connection closed.");
    };
  }

  _open();

  return {
    set(v: T) {
      if (sendOnSet && socket && socket.readyState === WebSocket.OPEN) {
        if (v instanceof Set) socket.send(JSON.stringify(Array.from(v)));
        else socket.send(typeof v === "string" ? v : JSON.stringify(v));
      }
      setStore(v);
    },
    update,
    subscribe,
  };
}

export function readableWebSocket<T extends object | string>(url: string, initialValue: T, wsc: wsConfig<T> = {}): Readable<T> {
  return {
    subscribe: writableWebSocket(url, initialValue, wsc).subscribe,
  };
}

export type asymConfig<T> = {
  f?: (x: ValidType) => T;
  beforeOpen?: () => Promise<void>;
  localStore?: Writable<LocalInfo>;
};

export interface AsymWritable<FromBack, ToBack> extends Omit<Writable<FromBack>, "set"> {
  set(v: ToBack): void;
}

export function asymWritableWebSocket<FromBack extends Sendable, ToBack extends Sendable | Set<Sendable>>(
  url: string,
  initialValue: FromBack,
  initialToBack: ToBack,
  { f = JSON.parse, beforeOpen, localStore }: asymConfig<FromBack> = {}
): AsymWritable<FromBack, ToBack> {
  let socket: WebSocket;
  let timeout: ReturnType<typeof setTimeout> | null;
  const { set: setFromBack, subscribe } = writable(initialValue); // fromback

  async function _open() {
    console.log("Connecting");
    timeout = null;
    if (beforeOpen) await beforeOpen();

    if (browser) {
      if (socket) socket.close();
      socket = new WebSocket(url);
      socket.onmessage = (event: MessageEvent): void => setFromBack(f(event.data as string));

      socket.onopen = () => {
        if (localStore) localStore.update((curr) => ({ ...curr, connected: true }));
        if (timeout) {
          clearTimeout(timeout);
          timeout = null;
        }
      };

      socket.onclose = () => {
        if (localStore) localStore.update((curr) => ({ ...curr, connected: false }));
        // eslint-disable-next-line @typescript-eslint/no-misused-promises
        if (!timeout) timeout = setTimeout(_open, 2000);
        console.error("Connection closed.");
      };
    }
  }

  _open().catch((e) => console.error(e));

  return {
    set(v: ToBack) {
      if (socket && socket.readyState === WebSocket.OPEN) {
        console.log();
        if (v instanceof Set) socket.send(JSON.stringify(Array.from(v)));
        else socket.send(typeof v === "string" ? v : JSON.stringify(v));
      }
    },
    update() {
      throw new Error("Cannot update an asymWritableWebSocket");
    },
    subscribe,
  };
}

export default writableWebSocket;
