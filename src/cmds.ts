export interface Cmd {
    op: string
}

export type Reagent = {
    name: string,
    port: number,
    v_pull: number,
    v_prime: number,
    v_push: number,
    wait: number
}

export const reagentDefault = {
    name: "",
    port: 1,
    v_pull: 100,
    v_prime: 200,
    v_push: 2000,
    wait: 26,
}

export type Pump = Cmd & {
    reagent: string,
    volume: number,
    op: "pump"
}

export type Prime = Cmd & {
    reagent: string,
    volume: number,
    op: "prime"
}

export type Temp = Cmd & {
    temp: number
    op: "temp"
}

export type Hold = Cmd & {
    time: number,
    temp: number,
    op: "hold"
}

export type Move = Cmd & {
    xy: [number, number],
    op: "move"
}


export type Image = Cmd & {
    xy_start: [number, number],
    xy_end: [number, number],
    z_tilt: number,
    channels: [boolean, boolean, boolean, boolean]
    laser_onoff: [boolean, boolean],
    lasers: [number, number],
    autofocus: boolean,
    op: "image"
}

export type Cmds = Pump | Prime | Temp | Hold | Move | Image
export type Ops = Cmds["op"]

export const defaults: { [key: string]: Cmds } = {
    "pump": { reagent: "", volume: 0, op: "pump" },
    "prime": { reagent: "", volume: 0, op: "prime" },
    "temp": { temp: 25, op: "temp" },
    "hold": { time: 0, temp: 25, op: "hold" },
    "move": { xy: [0, 0], op: "move" },
    "image": {
        xy_start: [0, 0], xy_end: [0, 0], z_tilt: 20000,
        channels: [true, true, true, true], laser_onoff: [true, true],
        lasers: [50, 50], autofocus: true, op: "image"
    }
}
