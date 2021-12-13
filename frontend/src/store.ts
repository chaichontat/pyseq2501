// From https://github.com/arlac77/svelte-websocket-store

import type { Subscriber, Unsubscriber, Updater, Writable } from "svelte/store"

/**
 * Create a writable store based on a web-socket.
 * Data is transferred as JSON.
 * Keeps socket open (reopens if closed) as long as there are subscriptions.
 * @param {string} url the WebSocket url
 * @param {string[]} socketOptions transparently passed to the WebSocket constructor
 * @return {Store}
 */
const reopenTimeouts = [2000, 5000, 10000, 30000, 60000];
type ValidType = string | ArrayBufferLike | Blob | ArrayBufferView;

export function websocketStore<T extends ValidType>(url: string, socketOptions?: string[]): Writable<T | null> {
    let socket: WebSocket | undefined
    let openPromise: Promise<boolean>
    let reopenTimeoutHandler: NodeJS.Timeout;
    let reopenCount: number = 0;

    const subscribers: Set<Subscriber<T | null>> = new Set();

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

        if (socket) {
            socket.close();
            socket = undefined;
        }
    }

    function reopen(): void {
        close();
        if (subscribers.size > 0) {
            reopenTimeoutHandler = setTimeout(() => open(), reopenTimeout());
        }
    }

    async function open(): Promise<any> {
        if (reopenTimeoutHandler) {
            clearTimeout(reopenTimeoutHandler);
            reopenTimeoutHandler = undefined;
        }

        // we are still in the opening phase
        if (openPromise) return openPromise;

        socket = new WebSocket(url, socketOptions);

        socket.onmessage = (event: MessageEvent): void => {
            // initialValue = JSON.parse(event.data);
            subscribers.forEach((subscriber) => {
                subscriber(event.data as T)
            });
        };

        socket.onclose = (_: CloseEvent): void => reopen();

        openPromise = new Promise((resolve, reject) => {
            socket.onerror = (error: Event): void => {
                reject(error);
                openPromise = undefined;
            };
            socket.onopen = (_: Event): void => {
                reopenCount = 0;
                resolve(true);
                openPromise = undefined;
            };
        });
        return openPromise;
    }

    return {
        set(value: T): void {
            const send = () => socket.send(value);
            if (socket.readyState !== WebSocket.OPEN) {
                open().then(send)
            } else { send() }
        },

        update(_: Updater<any>): void { },

        subscribe(subscriber: Subscriber<T | null>): Unsubscriber {
            open();
            subscriber(null);
            subscribers.add(subscriber);
            return () => {
                subscribers.delete(subscriber);
                if (subscribers.size === 0) {
                    close();
                }
            };
        }
    };
}

export default websocketStore;