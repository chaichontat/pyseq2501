# PySeq 2501 Web Interface

[![GitHub Actions](https://github.com/chaichontat/pyseq2501-web/actions/workflows/build_svelte.yml/badge.svg)](https://chaichontat.github.io/pyseq2501-web/)

This is the web interface and the communication system for [PySeq 2501](https://github.com/chaichontat/pyseq2501). Click on the badge above to see an example site!

## Usage

![2022-01-10 20 04 44](https://user-images.githubusercontent.com/34997334/148863230-8b66ae28-5212-4e1e-a74c-33ebe695be9f.gif)


## Installation
- Install [`pyseq2501`](https://github.com/chaichontat/pyseq2501)
    ```sh
    git clone https://github.com/chaichontat/pyseq2501
    conda env create -n pyseq -f environment.yml
    conda activate pyseq
    pip install pyseq2501/.
    ```


- Install [`npm`](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm).
- Clone this repo and run. The first command updates the `pyseq` environment.
    ```sh
    git clone https://github.com/chaichontat/pyseq2501-web
    cd pyseq2501-web
    conda env update -n pyseq -f environment.yml
    pip install .
    npm i
    npm run build
    ```

A [`tox`](https://tox.wiki/en/latest/) environment is available to make sure everything works.

## Run
```sh
pyseq2server --fake
```

```
Usage: pyseq2server [OPTIONS]

Options:
  -p, --port INTEGER  Port to run the server on (default: 8000).
  -h, --host TEXT     Hostname to bind to (default: localhost). Set 0.0.0.0
                      for network access.
  -o, --open          Open a web browser
  --fake              Use fake machine interface.
  --donothost         Only host the websocket, not the interface. Useful when
                      developing Svelte.
  --help              Show this message and exit.
```

The interface should be waiting for you at `http://localhost:8000/`!

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
