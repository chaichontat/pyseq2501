export interface Cmd {
    op: string
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
    wait: boolean
    op: "temp"
}

export type Hold = Cmd & {
    time: number,
    op: "hold"
}

export type TakeImage = Cmd & {
    name: string,
    path: string,
    xy0: [number, number],
    xy1: [number, number],
    channels: [boolean, boolean, boolean, boolean]
    z_tilt: number | [number, number, number],
    laser_onoff: [boolean, boolean]
    lasers: [number, number]
    z_obj: number,
    z_spacing?: number,
    z_n?: number,
    od: [number, number],
    overlap: number,
    save: boolean
    op: "takeimage"
}

export type Autofocus = Cmd & {
    channels: [boolean, boolean, boolean, boolean]
    laser_onoff: boolean,
    laser: number,
    od: number
    op: "autofocus"
}

export type Goto = Cmd & {
    step: number,
    n: number,
    op: "goto"
}

export type Cmds = Pump | Prime | Temp | Hold | TakeImage | Autofocus | Goto
export type Ops = Cmds["op"]

export type CmdDefaults = { "pump": Pump, "prime": Prime, "temp": Temp, "hold": Hold, "takeimage": TakeImage, "autofocus": Autofocus, "goto": Goto }

export const cmdDefaults: Readonly<CmdDefaults> = {
    "pump": { reagent: "", volume: 0, op: "pump" },
    "prime": { reagent: "", volume: 0, op: "prime" },
    "temp": { temp: 25, wait: true, op: "temp" },
    "hold": { time: 0, op: "hold" },
    "takeimage": {
        name: "Test",
        path: ".",
        xy0: [0, 0],
        xy1: [1, 1],
        channels: [true, true, true, true], z_tilt: 19850, z_obj: 32000, save: false,
        lasers: [0, 0], laser_onoff: [true, true], od: [0, 0], overlap: 0.1, op: "takeimage"
    },
    "autofocus": {
        channels: [true, true, true, true], laser_onoff: true,
        laser: 5, od: 0, op: "autofocus"
    },
    "goto": { step: 1, n: 4, op: "goto" }
}

const p = cmdDefaults