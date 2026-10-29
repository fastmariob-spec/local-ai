# Getting started

How to set up this project from scratch on a new machine (the 3070 Ti desktop or the 5090).
Everything runs inside **WSL2 Ubuntu 24.04**. If WSL isn't installed yet, do [WSL setup](#wsl-setup) at the bottom first.

## 1. Check the GPU from WSL

Open an Ubuntu terminal and run:

```bash
nvidia-smi
```

You should see your GPU listed. If the command fails, fix the Windows NVIDIA driver first (see [WSL setup](#wsl-setup)). **Never install an NVIDIA driver inside WSL.**

## 2. Install uv

[uv](https://docs.astral.sh/uv/) manages Python and the locked environment. It installs to `~/.local/bin` and doesn't need sudo.

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Open a new terminal (or run `source ~/.bashrc`) and check it:

```bash
uv --version
```

If `uv` isn't found, add `export PATH=$HOME/.local/bin:$PATH` to `~/.bashrc`.

## 3. Configure git

```bash
git config --global user.name "Your Name"
git config --global user.email you@example.com

# Use the Windows Git Credential Manager for GitHub logins (requires Git for Windows)
git config --global credential.helper "/mnt/c/Program\ Files/Git/mingw64/bin/git-credential-manager.exe"
```

The first push or pull opens a GitHub sign-in in your browser. After that, the login is remembered.

## 4. Clone and build the environment

Keep the project in the Linux filesystem (`~/...`), never under `/mnt/c/...`.

```bash
mkdir -p ~/projects
git clone https://github.com/fastmariob-spec/local-ai.git ~/projects/local-ai
cd ~/projects/local-ai
uv sync
```

`uv sync` creates `.venv/` from `uv.lock`, so every machine gets exactly the same packages:
fastai 2.8.12, PyTorch 2.14.1 with CUDA 13.0 (supports the 5090's sm_120), JupyterLab and timm.
The install is about 6 GB. Check free space on C: first (see [Disk space](#disk-space)).

## 5. Verify

```bash
uv run python scripts/check_env.py
```

Expected output (3070 Ti shown):

```
torch 2.14.1+cu130 (CUDA 13.0), fastai 2.8.12
GPU: NVIDIA GeForce RTX 3070 Ti, sm_86, 6.9 / 8.0 GiB free
fp16 matmul OK: True
WSL disk free: 948 GiB
C: drive free (real limit): 56 GiB
```

On the 5090 it should show `sm_120` and about 32 GiB.

## 6. Register the Jupyter kernel

This lets VS Code and other Jupyter frontends find the environment:

```bash
uv run python -m ipykernel install --user --name local-ai --display-name "Python 3 (local-ai)"
```

## 7. Run notebooks

**JupyterLab:**

```bash
cd ~/projects/local-ai
uv run jupyter lab --no-browser
```

Then open the `http://localhost:8888/...` link it prints in your Windows browser.

**VS Code:** see [Running notebooks in VS Code](#running-notebooks-in-vs-code) below.

## Running notebooks in VS Code

On Windows, install VS Code and its **WSL** extension (by Microsoft).

### 1. Open the project from WSL, not from Windows

In an Ubuntu terminal:

```bash
cd ~/projects/local-ai
code .
```

Don't open it through File → Open in Windows, or with a `\\wsl$\...` path. That runs VS Code in Windows mode, where the Linux `.venv` can't be used.

**Check:** the bottom-left corner shows a blue **`WSL: Ubuntu-24.04`** label. If it doesn't, click that corner and choose **Connect to WSL**, then open `~/projects/local-ai`.

### 2. Install the extensions inside WSL

Extensions installed in Windows VS Code don't carry over into a WSL window. Without them, a notebook won't run or find a kernel there.

1. Open the Extensions panel (`Ctrl+Shift+X`).
2. Search **Python** (by Microsoft). If it's already installed in Windows, it shows a button **"Install in WSL: Ubuntu-24.04"**. Click it.
3. Do the same for **Jupyter** (by Microsoft).
4. When prompted, reload the window (or press `Ctrl+Shift+P` and run **Developer: Reload Window**).

**Check:** in the Extensions panel, both appear under a section named **WSL: UBUNTU-24.04 – INSTALLED**.

### 3. Choose the project's Python interpreter

1. Press `Ctrl+Shift+P` and run **Python: Select Interpreter**.
2. Choose **`./.venv/bin/python`** (it may be labelled "Python 3.12.3 ('.venv')").
3. If it isn't listed, choose **Enter interpreter path…** and type `~/projects/local-ai/.venv/bin/python`.

### 4. Open the notebook and pick the kernel

1. Open `nbs/00_template.ipynb`.
2. Click **Select Kernel** in the top-right of the notebook.
3. Choose **Python Environments… → .venv**, or **Jupyter Kernel… → Python 3 (local-ai)**. Both use the same Python. The second one only appears after [step 6](#6-register-the-jupyter-kernel) above.

**Check:** the top-right of the notebook shows `.venv (Python 3.12.3)` or `Python 3 (local-ai)`.

### 5. Run the cells

Run the config cell, then the imports cell (`Shift+Enter`). The first fastai import takes about 10–20 seconds. It should print your GPU and settings, e.g.:

```
NVIDIA GeForce RTX 3070 Ti | BS 32 | IMG_SIZE 224 | FP16 True
```

### Troubleshooting

| Symptom | Fix |
|---|---|
| No `WSL:` label bottom-left | Install the **WSL** extension in Windows VS Code, then repeat step 1 |
| "Install in WSL" button missing | You're not in a WSL window. Go back to step 1 |
| Kernel list is empty or spins forever | Run **Developer: Reload Window**, then **Jupyter: Select Interpreter to Start Jupyter Server** and choose `.venv` |
| `ModuleNotFoundError: fastai` | The wrong kernel is selected (for example the system `/usr/bin/python3`). Redo step 4 |
| Kernel dies on the import cell | Run `uv run python scripts/check_env.py` in a terminal and check its output |

## Working in the project

- **New notebook:** copy `nbs/00_template.ipynb`. The first code cell holds `BS`, `IMG_SIZE` and `FP16`. The defaults fit 8 GB, so raise them there on the 5090.
- **Data and weights** go in `data/` and `models/`. Both are git-ignored. fastai downloads go to `data/fastai`. To keep them somewhere else, set `LOCAL_AI_DATA` / `LOCAL_AI_MODELS`.
- **Adding a package:** run `uv add <package>`, then commit both `pyproject.toml` and `uv.lock`. On the other machine, run `git pull && uv sync`.
- **Don't upgrade torch casually.** Keep it at a version fastai supports, with a CUDA 12.8+ build for the 5090.

## Disk space

WSL's virtual disk reports far more free space than actually exists. The real limit is free space on the Windows C: drive, and `check_env.py` prints both. To free space:

```bash
uv cache clean                       # uv's package cache
du -sh data/* models/* 2>/dev/null   # find large datasets / checkpoints
```

Deleting files inside WSL doesn't shrink the virtual disk file on C: by itself. To give the space back to Windows, run `wsl --shutdown`, then compact the `.vhdx` file. One way is `Optimize-VHD` in an admin PowerShell. It needs Hyper-V, which Windows Home doesn't include. The other is `diskpart` → `select vdisk file="<path>\ext4.vhdx"` → `compact vdisk`.

---

## WSL setup

Do this once per Windows machine, before the steps above.

### 1. Install the NVIDIA driver on Windows

Install the latest **Game Ready** or **Studio** driver for your GPU from nvidia.com (or the NVIDIA app), on **Windows**. This driver also provides the GPU to WSL.
Do **not** install any NVIDIA or CUDA driver inside Ubuntu. CUDA comes with the PyTorch wheels.

### 2. Install WSL2 with Ubuntu 24.04

In an **administrator PowerShell**:

```powershell
wsl --install -d Ubuntu-24.04
```

Reboot when asked. Ubuntu then opens and asks for a Linux username and password. Afterwards, check that it's running WSL **2**:

```powershell
wsl --update
wsl -l -v        # VERSION column must say 2
```

Use the same Ubuntu release and the same project path (`~/projects/local-ai`) on both machines.

### 3. Set memory and swap limits

Create `%USERPROFILE%\.wslconfig` on Windows (e.g. `C:\Users\<you>\.wslconfig`). Size it to that machine's RAM and leave some for Windows. Example for the 32 GB desktop:

```ini
[wsl2]
memory=24GB
swap=8GB
```

Apply it from PowerShell with `wsl --shutdown`, then reopen Ubuntu. Inside WSL, `free -h` shows the new limit.

### 4. Basic packages

In Ubuntu:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git curl build-essential
```

Then go back to [step 1](#1-check-the-gpu-from-wsl).
