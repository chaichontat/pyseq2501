// From https://github.com/arlac77/svelte-websocket-store

import { Subscriber, Unsubscriber, Updater, Readable, Writable, writable } from "svelte/store"
/**
 * Create a writable store based on a web-socket.
 * Data is transferred as JSON.
 * Keeps socket open (reopens if closed) as long as there are subscriptions.
 * @param {string} url the WebSocket url
 * @param {string[]} socketOptions transparently passed to the WebSocket constructor
 * @return {Store}
 */
const reopenTimeouts = [2000, 5000, 10000, 30000, 60000];
type ValidType = string; // | ArrayBufferLike | Blob | ArrayBufferView;

// TODO Asymmetric store.
export function websocketStore<T>(url: string, value: T, f: (x: ValidType) => any = (x: ValidType) => x, broadcastSet: boolean = true): Writable<T> {
    // console.log(`%cInitializing ${ url }.`, "color:green")
    let socket: WebSocket
    let openPromise: Promise<boolean>
    let reopenTimeoutHandler: ReturnType<typeof setTimeout> | undefined;
    let reopenCount: number = 0;
    let t0 = Date.now()

    const subscribers: Set<Subscriber<T>> = new Set();

    function reopenTimeout(): number {
        const n = reopenCount;
        reopenCount++;
        return reopenTimeouts[
            n >= reopenTimeouts.length - 1 ? reopenTimeouts.length - 1 : n
        ];
    }

    function close(): void {
        if (reopenTimeoutHandler) {
            clearTimeout(reopenTimeoutHandler);
        }

        if (socket.readyState !== WebSocket.CLOSED) {
            socket.close();
        }
    }

    function reopen(): void {
        close();
        if (subscribers.size > 0) {
            reopenTimeoutHandler = setTimeout(() => open(), reopenTimeout());
        }
    }

    async function open(): Promise<boolean> {
        if (reopenTimeoutHandler) {
            clearTimeout(reopenTimeoutHandler);
            reopenTimeoutHandler = undefined;
        }

        // we are still in the opening phase
        // if (socket.readyState === WebSocket.CONNECTING || socket.readyState === WebSocket) return openPromise;

        socket = new WebSocket(url);
        socket.onmessage = (event: MessageEvent): void => {
            console.log(event.data)
            subscribers.forEach((subscriber) => {
                // @ts-ignore
                value = f(event.data)
                subscriber(value)
            });
        };

        socket.onclose = (_: CloseEvent): void => (reopen())

        openPromise = new Promise((resolve, reject) => {
            socket.onerror = (error: Event): void => {
                console.error("Websocket error")
                reject(error);
            };
            socket.onopen = (_: Event): void => {
                reopenCount = 0;
                t0 = Date.now()
                resolve(true);
            };
        });
        return openPromise;
    }

    open();

    return {
        set(value: T): void {
            console.log(value)
            const send =
                (typeof value == "object")
                    ? () => socket.send(JSON.stringify(value))
                    // @ts-ignore
                    : () => socket.send(value)

            if (socket) {
                switch (socket.readyState) {
                    case WebSocket.CLOSED || WebSocket.CLOSING: {
                        open().then(send)
                        break;
                    }
                    case WebSocket.CONNECTING: {
                        openPromise.then(send)
                        break;
                    }
                    case WebSocket.OPEN: {
                        send()
                        break;
                    }
                }
            }

            if (broadcastSet) {
                subscribers.forEach((subscriber: Subscriber<T>) => (subscriber(value)));
            }
        },

        update(updater: Updater<T>) { subscribers.forEach((subscriber) => subscriber(updater(value))) },

        subscribe(subscriber: Subscriber<T>): Unsubscriber {
            subscriber(value);
            subscribers.add(subscriber);
            return () => (subscribers.delete(subscriber))
        }
    };
}

export default websocketStore;


class WebSocketStore<T> {
    protected ws: WebSocket
    #subscribers: Set<Subscriber<T>>


    constructor (url: string) {
        const { subscribe, set, update } = writable(0);
        this.ws = new WebSocket(url);
        this.#subscribers = new Set();
    }
}