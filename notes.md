# Notes and Logs

## November 2021

### Nov 10th

- Updated system to Windows 10 to prevent [this](https://www.fbi.gov/scams-and-safety/common-scams-and-crimes/ransomware). Seems to break [HiSeq Control Software](https://support.illumina.com/sequencing/sequencing_instruments/hiseq_2500/downloads.html) v2.2.68 which checks at launch if it is being run on Windows Vista.
- Installed [`miniforge`](https://github.com/conda-forge/miniforge/releases/tag/4.10.3-7) and created environment for [pyseq2500](https://github.com/nygctech/PySeq2500)
  - Need [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/). Installed with default settings.
  - Somehow `scikit-learn` is set to compile from scratch which took quite a while (~30 minutes).
- `pip install pyqt5-tools`

### Nov 12nd

```sh
conda create -n hiseq python=3.8
conda activate hiseq
pip install pyseq2500 --user
pip install wmi --user
pip install pyqt5-tools --user
pip uninstall pywin32
conda install pywin32
```
