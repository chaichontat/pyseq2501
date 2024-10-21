/// <reference types="@sveltejs/kit" />

declare type DndEvent = import("svelte-dnd-action").DndEvent;
declare namespace svelte.JSX {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  interface HTMLAttributes<T> {
    onconsider?: (event: CustomEvent<DndEvent> & { target: EventTarget & T }) => void;
    onfinalize?: (event: CustomEvent<DndEvent> & { target: EventTarget & T }) => void;
  }
}