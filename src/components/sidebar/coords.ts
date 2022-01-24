import type { XY } from "$src/store";

const Y_UPPER = -180000;
const A_LEFT = 7331;
const B_LEFT = 33070;
const X_STEP_MM = 409.6;
const Y_STEP_MM = 1e5;

export function raw_to_local(flowcell: boolean, x: number, y: number): XY {
    const x_offset = flowcell ? B_LEFT : A_LEFT;
    return {
        x: (x - x_offset) / X_STEP_MM,
        y: (y - Y_UPPER) / Y_STEP_MM,
    };
}

export function local_to_raw(flowcell: boolean, x: number, y: number): XY {
    const x_offset = flowcell ? B_LEFT : A_LEFT;
    return {
        x: x * X_STEP_MM + x_offset,
        y: y * Y_STEP_MM + Y_UPPER
    }
}
