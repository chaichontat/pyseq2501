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

A lot of problems with `win32api DLL`. Probably from different versions

### Nov 16th
- Installed
  - Windows Management Engine 5.1
  - PowerShell 7.2
  - Chocolatey
  - Node.js v15.8.0 (see [this](https://stackoverflow.com/questions/62212754/nodejs-for-windows-7))
  - OpenSSH-[win32](https://github.com/PowerShell/Win32-OpenSSH/releases). Don't forget to open port 22 for `sshd`. Default password is `sbs123`.
  - VSCode Server
    - Set `AllowTcpForwarding yes` in `%ALLUSERSPROFILE%\ssh\sshd_config`.
    - See https://superuser.com/questions/1451241/command-to-copy-client-public-key-to-windows-openssh-sftp-ssh-server-authorized to set public key authentication.
      - TL;DR Copy your `id_rsa.pub` to `%ALLUSERSPROFILE%\ssh\administrators_authorized_keys`.


### Nov 17th
- Forum https://forum.hackteria.org/c/reseq/19

Bring back Windows 10 Users must enter password box in `control userpasswords2`

```
reg ADD “HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\PasswordLess\Device” /v DevicePasswordLessBuildVersion /t REG_DWORD /d 0 /f
```

Deal with intermittent SSH connectivity issues
```json
"remote.SSH.enableDynamicForwarding": false
```
