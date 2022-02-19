export type Reagent = {
    name: string,
    port: number,
    v_pull: number,
    v_prime: number,
    v_push: number,
    wait: number
}

export type ReagentGroup = {
    name: string
}

export const reagentDefault = {
    name: "",
    port: 1,
    v_pull: 100,
    v_prime: 200,
    v_push: 2000,
    wait: 26,
}