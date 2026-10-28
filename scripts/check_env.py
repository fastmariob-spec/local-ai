"""Sanity-check the environment: GPU visible, fp16 matmul works, disk headroom."""
import shutil
from pathlib import Path

import torch
import fastai

PROJECT = Path(__file__).resolve().parents[1]

print(f"torch {torch.__version__} (CUDA {torch.version.cuda}), fastai {fastai.__version__}")
assert torch.cuda.is_available(), "CUDA not available: check the Windows NVIDIA driver"

props = torch.cuda.get_device_properties(0)
free, total = torch.cuda.mem_get_info()
print(f"GPU: {props.name}, sm_{props.major}{props.minor}, "
      f"{free / 2**30:.1f} / {total / 2**30:.1f} GiB free")

x = torch.randn(1024, 1024, device="cuda", dtype=torch.float16)
print("fp16 matmul OK:", (x @ x).float().abs().mean().item() > 0)

# WSL's virtual disk reports far more space than C: actually has; check the host side too.
print(f"WSL disk free: {shutil.disk_usage(PROJECT).free / 2**30:.0f} GiB")
c_drive = Path("/mnt/c")
if c_drive.exists():
    print(f"C: drive free (real limit): {shutil.disk_usage(c_drive).free / 2**30:.0f} GiB")
