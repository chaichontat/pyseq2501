# PySeq2501

[![GitHub Actions](https://github.com/chaichontat/goff-rotation/actions/workflows/python-package-conda.yml/badge.svg)](https://github.com/chaichontat/goff-rotation/actions/workflows/python-package-conda.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Control your HiSeq 2000/2500 with ease. Web control available [here](https://github.com/chaichontat/pyseq2501-web).

## Installation
This package is written for Python 3.9+ and requires Windows 10 to function. For those using Windows 7, you can perform a [dual-boot](https://www.techadvisor.com/how-to/windows/how-dual-boot-windows-3633084/) installation on any other partitions relatively easily.

The only required custom driver is the Illumina/Hamamatsu ActiveSilicon [driver](https://github.com/chaichontat/pyseq2501/tree/main/driver).

Using conda,
```bash
conda env create -n pyseq -f environment.yml
pip install -e .
```

## Usage

Example scripts are in the [`scripts/`](https://github.com/chaichontat/pyseq2501/tree/main/scripts) folder.
