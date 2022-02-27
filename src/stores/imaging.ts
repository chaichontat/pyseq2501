export type Hist = {
    counts: number[],
    bin_edges: number[]
}

export type Img = {
    n: number,
    img: string[],
    hist: Hist[],
    channels: [boolean, boolean, boolean, boolean],
    dim: [number, number],
}

export const imgDefault: Readonly<Img> = { n: 0, img: [""], hist: [{ counts: [10], bin_edges: [0] }], channels: [false, false, false, false], dim: [0, 0] }
