export type FCState = {
    running: boolean,
    step: number,
    msg: string
}

export const fcStateDefault: Readonly<FCState> = { running: false, step: 0, msg: "" }

export type Status = {
    x: number;
    y: number;
    z_tilt: [number, number, number];
    z_obj: number;
    laser_onoff: [boolean, boolean];
    lasers: [number, number];
    shutter: boolean;
    od: [number, number];
    fcs: [FCState, FCState],
    block: "" | "moving" | "capturing" | "previewing"
    msg: string;
};

export const statusDefault: Readonly<Status> = {
    x: -1,
    y: -1,
    z_tilt: [-1, -1, -1],
    z_obj: -1,
    od: [0., 0.],
    laser_onoff: [true, true],
    lasers: [-1, -1],
    shutter: false,
    fcs: [{ ...fcStateDefault }, { ...fcStateDefault }],
    block: "",
    msg: "Idle",
};