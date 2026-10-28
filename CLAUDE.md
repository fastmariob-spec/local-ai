# local-ai

Workspace for working through **course.fast.ai** (Part 1 and Part 2) and for running/fine-tuning AI models locally.

## Machines

Two machines are used. Code and notebooks must run on both without edits.

| | Primary (this machine) | Heavy machine |
|---|---|---|
| GPU | RTX 3070 Ti, 8 GB VRAM (~6.5 GB usable; Windows desktop holds ~1.4 GB) | RTX 5090, 32 GB VRAM (Blackwell, sm_120) |
| CPU / RAM | i9-10900X 10c/20t, 32 GB | — |
| OS | Windows 11 Home + WSL2 Ubuntu | Windows + WSL2 Ubuntu |
| Disk | Single C: drive, ~67 GB free — tight | — |
| Role | Day-to-day: course notebooks, small experiments, 7–9B quantized LLM inference | Expensive runs: large batches, long training, Stable Diffusion, LLM fine-tuning, models >14B |

### When to switch to the 5090
Suggest moving a job to the 5090 instead of squeezing it onto the 3070 Ti when it:
- needs more than ~6 GB VRAM even with fp16 and small batch sizes,
- trains for more than roughly an hour,
- fine-tunes a 7B+ LLM, or runs inference on a 14B+ model,
- needs large datasets that would use up the remaining disk on C:.

Don't spend time working around VRAM limits (gradient checkpointing, tiny batches, aggressive quantization) for these jobs. Recommend the switch instead.

## Environment (both machines)

Both machines use the same setup, so these rules apply to each.

- Everything runs inside **WSL2 Ubuntu**, not native Windows.
- **Never install an NVIDIA Linux driver inside WSL.** The Windows driver provides the GPU to WSL. CUDA comes from the PyTorch wheels.
- Keep the project and data in the Linux filesystem (`~/...`). Don't put them under `/mnt/c/...`, because reading files across that boundary is very slow.
- Memory/swap limits for WSL go in `%USERPROFILE%\.wslconfig` on each machine. Size them to that machine's RAM.
- Use the same Ubuntu release and the same project path inside WSL (e.g. `~/projects/local-ai`) on both machines, so environments and paths match.
- Run Jupyter inside WSL and open it at `http://localhost:8888` from the Windows browser, or use VS Code with Remote-WSL.
- Install the PyTorch version fastai currently supports, not necessarily the newest one.
- The 5090 (Blackwell) needs PyTorch built with CUDA 12.8 or newer. Older wheels don't support sm_120.

## Working conventions

- **Portability between machines:**
  - No hardcoded absolute paths. Use `pathlib` and paths relative to the project or an env var.
  - Pin dependencies in a lock or requirements file so both machines build the same environment.
  - Don't commit datasets, model weights, or checkpoints. Keep them in git-ignored folders (e.g. `data/`, `models/`).
- **Set notebook parameters at the top:** batch size, image size, and precision go in one config cell so they can be bumped up on the 5090 without hunting through the code. Default to values that fit 8 GB (e.g. `bs=32` or smaller, `.to_fp16()`).
- **Disk is scarce on this machine.** Check free space before downloading large datasets or models, and clean up old checkpoints and unused conda/pip caches.
- Before long runs, state which machine the job is meant for.
- Kaggle and Colab remain an option for course notebooks that are built around Kaggle competitions.
