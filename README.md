# PySeq2501

[![GitHub Actions](https://github.com/chaichontat/goff-rotation/actions/workflows/python-package-conda.yml/badge.svg)](https://github.com/chaichontat/goff-rotation/actions/workflows/python-package-conda.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Control your HiSeq 2000/2500 with ease. Web control (under development) available [here](https://github.com/chaichontat/pyseq2501-web).

Fluidics control coming soon!

## Installation
This package is written for Python 3.9+ and requires Windows 10 to function. For those using Windows 7, you can perform a [dual-boot](https://www.techadvisor.com/how-to/windows/how-dual-boot-windows-3633084/) installation on any other partitions relatively easily.

The only required custom driver is the Illumina/ActiveSilicon [driver](https://github.com/chaichontat/pyseq2501/tree/main/driver) which functions in both Windows 7 and Windows 10.

Using conda,
```bash
conda env create -n pyseq -f environment.yml
pip install -e .
```

## Usage

Example scripts are in the [`scripts/`](scripts) folder. The showcase is `take_image.py`(scripts/take_image.py) which demonstrates fast image capture and autofocus.
