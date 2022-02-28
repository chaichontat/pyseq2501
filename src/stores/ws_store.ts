import { browser } from "$app/env";
import { Readable, Writable, writable } from "svelte/store";
import type { LocalInfo } from "./store";

type ValidType = string; // | ArrayBufferLike | Blob | ArrayBufferView;

export type wsConfig = {
    f?: (x: ValidType) => any
    beforeOpen?: () => Promise<void>,
    localStore?: Writable<LocalInfo>
    sendOnSet?: boolean
}

export function writableWebSocket<T extends object | string>(url: string, initialValue: T,
    { f = JSON.parse, beforeOpen, localStore, sendOnSet = true }: wsConfig = {}): Writable<T> {
    let socket: WebSocket
    let timeout: ReturnType<typeof setTimeout> | null
    const { set: setStore, subscribe, update } = writable(initialValue)

    async function _open() {
        console.log("Connecting")
        timeout = null

        socket = new WebSocket(url);
        socket.onmessage = (event: MessageEvent): void => (setStore(f(event.data)))

        socket.onopen = async () => {
            if (beforeOpen) await beforeOpen()
            if (localStore) localStore.update((curr) => ({ ...curr, connected: true }))
            if (timeout) {
                clearTimeout(timeout)
                timeout = null
            }
        }

        socket.onclose = () => {
            if (localStore) localStore.update((curr) => ({ ...curr, connected: false }))
            if (!timeout) timeout = setTimeout(_open, 2000)
            console.error("Connection closed.")
        }
    }

    _open();

    return {
        set(v: T) {
            if (sendOnSet && socket && socket.readyState === WebSocket.OPEN) {
                socket.send(typeof v === "object" ? JSON.stringify(v) : v)
            }
            setStore(v);
        },
        update,
        subscribe,
    };
}

export function readableWebSocket<T extends object | string>(url: string, initialValue: T, wsc: wsConfig = {}): Readable<T> {
    return {
        subscribe: writableWebSocket(url, initialValue, wsc).subscribe
    }
}

export type asymConfig<T> = {
    f?: (x: ValidType) => T,
    beforeOpen?: () => Promise<void>,
    localStore?: Writable<LocalInfo>
}

export interface AsymWritable<FromBack, ToBack> extends Omit<Writable<FromBack>, "set"> {
    set(v: ToBack): void
}

export function asymWritableWebSocket<FromBack extends object | string, ToBack extends object>(url: string, initialValue: FromBack, initialToBack: ToBack,
    { f = JSON.parse, beforeOpen, localStore }: asymConfig<FromBack> = {}): AsymWritable<FromBack, ToBack> {
    let socket: WebSocket
    let timeout: ReturnType<typeof setTimeout> | null
    const { set: setFromBack, subscribe } = writable(initialValue) // fromback

    async function _open() {
        console.log("Connecting")
        timeout = null
        if (beforeOpen) await beforeOpen()

        if (browser) {
            if (socket) socket.close()
            socket = new WebSocket(url);
            socket.onmessage = (event: MessageEvent): void => (setFromBack(f(event.data)))

            socket.onopen = () => {
                if (localStore) localStore.update((curr) => ({ ...curr, connected: true }))
                if (timeout) {
                    clearTimeout(timeout)
                    timeout = null
                }
            }

            socket.onclose = () => {
                if (localStore) localStore.update((curr) => ({ ...curr, connected: false }))
                if (!timeout) timeout = setTimeout(_open, 2000)
                console.error("Connection closed.")
            }
        }
    }

    _open();

    return {
        set(v: ToBack) {
            if (socket && socket.readyState === WebSocket.OPEN) {
                console.log();

                socket.send(typeof v === "object" ? JSON.stringify(v) : v)
            }
        },
        update() { throw new Error("Cannot update an asymWritableWebSocket") },
        subscribe,
    };
}

export default writableWebSocket;

