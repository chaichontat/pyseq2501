From the logs, there are 3 methods of taking images.

## Focus Stack
This uses the partial area mode of the camera to take 232 frames of 10,240 pixels each, which I'm guessing to be 2048 × 5 pixels. There are probably 4 modes of trigger:

1. Unknown
2. `ZYT 0 2` Start $z$-ramp when first camera image trigger pulse is sent (past camera clearing lines).
3. `ZYT 0 3` Start $z$-ramp and trigger camera immediately.
4. `ZYT {y} 4` Start $z$-ramp when $y$ reaches `{y}`.

## Small TDI
`TDIYARM 2` This is probably used to generate thumbnails. Generate image of size 4096 × 2688 pixels.

## Large TDI
`TDIYARM 3` Production run. Image the entire flow cell, generate image of size 4096 × 160000 pixels.
