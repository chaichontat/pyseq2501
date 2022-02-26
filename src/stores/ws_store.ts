import { Readable, Writable, writable } from "svelte/store";
import type { LocalInfo } from "./store";

type ValidType = string; // | ArrayBufferLike | Blob | ArrayBufferView;

export type wsConfig = {
    f?: (x: ValidType) => any
    broadcastOnSet?: boolean,
    beforeOpen?: () => Promise<void>,
    localStore?: Writable<LocalInfo>
}

export function writableWebSocket<T extends object | string>(url: string, initialValue: T,
    { f = JSON.parse, broadcastOnSet, beforeOpen, localStore }: wsConfig = {}): Writable<T> {
    // console.log(`%cInitializing ${ url }.`, "color:green")
    let socket: WebSocket
    let timeout: ReturnType<typeof setTimeout> | null
    const { set, subscribe, update } = writable(initialValue)

    async function _open() {
        if (beforeOpen) await beforeOpen()

        socket = new WebSocket(url);
        socket.onmessage = (event: MessageEvent): void => {
            console.log(event.data)
            set(f(event.data))
        };

        socket.onopen = () => {
            if (localStore) localStore.update((curr) => ({ ...curr, connected: true }))
            if (timeout) {
                clearTimeout(timeout)
                timeout = null
            }
        }

        socket.onclose = () => {
            if (localStore) localStore.update((curr) => ({ ...curr, connected: false }))
            if (timeout) timeout = setTimeout(_open, 1000)
        }
    }

    set(initialValue)
    _open();

    return {
        set(v: T) {
            if (socket && socket.readyState === WebSocket.OPEN) {
                socket.send(typeof v === "object" ? JSON.stringify(v) : v)
            }

            if (broadcastOnSet) set(v);
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

export default writableWebSocket;


class WebSocketStore<T> {
    protected ws: WebSocket | null
    protected url: string
    protected f: (arg0: string) => T
    #timeout: ReturnType<typeof setTimeout> | null
    protected wr: Writable<T>

    constructor (url: string, value: T, f = JSON.parse) {
        this.wr = writable(value);
        this.url = url
        this.f = f
        this.#timeout = null
        this.ws = null
        this._open()
    }

    _open() {
        this.ws = new WebSocket(this.url);
        this.ws.onopen = () => {
            if (this.#timeout)
                clearTimeout(this.#timeout)

        }
        this.ws.onmessage = (event: MessageEvent) => (this.wr.set(this.f(event.data)));

        this.ws.onclose = () => {
            if (!this.#timeout)
                this.#timeout = setTimeout(this._open, 5000)
        }
    }

}


