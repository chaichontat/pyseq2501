# PySeq 2501 Web Interface

[![GitHub Actions](https://github.com/chaichontat/pyseq2501-web/actions/workflows/build_svelte.yml/badge.svg)](https://chaichontat.github.io/pyseq2501-web/)

This is the web interface and the communication system for [PySeq 2501](https://github.com/chaichontat/pyseq2501). Click on the badge above to see an example site!

## Usage

![2022-01-10 20 04 44](https://user-images.githubusercontent.com/34997334/148863230-8b66ae28-5212-4e1e-a74c-33ebe695be9f.gif)


## Installation
Install [`npm`](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm) and clone this repo.

Run
```sh
npm i
npm run build
npm run preview
```

## Sequence

```mermaid
sequenceDiagram
    participant FastAPI
    participant Experiment
        loop Every 5 seconds or when log is available
            Imager-->FastAPI: State
            FastAPI-->Camera: Log
        end

    FastAPI->>Experiment: run
    Note right of FastAPI: with userSettings as TakeImage

    Experiment->>Imager: run
    Note right of Experiment: Divide x and z into <br> multiple take commands
    Imager->>Camera: Start acquisition
    activate Camera

    loop every 2 bundles
        Camera->>FastAPI: "N bundles captured"
    end

    Camera->>Imager: All bundles captured
    deactivate Camera
    Imager->>FastAPI: Image
    Note right of FastAPI: "imgReady" via cmdStore<br> with image through GET

    
```
