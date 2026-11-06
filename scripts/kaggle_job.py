"""Điều khiển các task GPU trên Kaggle bằng Kaggle CLI (theo mẫu Lab2/kaggle/build_gfp_kernel.py).

  python scripts/kaggle_job.py upload                    # đóng gói data/kaggle_pack → dataset riêng tư
  python scripts/kaggle_job.py push --task crossenc      # sinh kernel + push (GPU, internet)
  python scripts/kaggle_job.py wait --task crossenc      # đợi complete/error
  python scripts/kaggle_job.py pull --task crossenc      # tải output về results/kaggle/<task>/
  python scripts/kaggle_job.py all --task crossenc       # push + wait + pull
Thêm --smoke để chạy thử trên 3 truy vấn mỗi tập.
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.data import pack as packmod  # noqa: E402
from src.utils.paths import PACK, RESULTS  # noqa: E402

OWNER = "hoangducchung"
DATASET = f"{OWNER}/biorerank-pack"
KERNELS = ROOT / "kaggle" / "kernels"
TASKS = {
    # task: (gpu, kernel_sources, env)
    "crossenc": (True, [], {}),
    "medcpt_feat": (True, [], {}),
    "biowordvec_cut": (False, [], {}),
    "bilstm": (True, ["biowordvec_cut"], {}),
    # kiểm E0: cấu hình giống Rankify (bài báo) — chỉ abstract, fp32, không cắt 512 với cross-encoder
    "crossenc_rankify": (True, [], {"CE_DOCFMT": "text", "CE_FP32": "1", "CE_MAXLEN": "model", "CE_TAG": ".rk",
                                     "CE_SETS": "trec-covid,nfcorpus,scifact", "CE_E2": "0",
                                     "CE_MODELS": "bge_v2_m3,monot5_base,bge_base,bge_large,mxbai_base", "CE_BATCH": "16"}),
}
TASK_MODULE = {"crossenc_rankify": "crossenc"}


def slug(task):
    return "biorerank-" + task.replace("_", "-")


def kaggle(*args, check=True, capture=False):
    cmd = ["kaggle", *map(str, args)]
    print("$", " ".join(cmd), flush=True)
    r = subprocess.run(cmd, check=False, text=True, capture_output=capture)
    if check and r.returncode != 0:
        raise SystemExit(f"Lỗi Kaggle CLI ({r.returncode}): {(r.stderr or '')[-500:]}")
    return r


def upload(msg="update"):
    if not (PACK / "PACK_MANIFEST.json").exists():
        packmod.build()
    meta = {"title": "biorerank-pack", "id": DATASET, "licenses": [{"name": "other"}]}
    (PACK / "dataset-metadata.json").write_text(json.dumps(meta, indent=1))
    exists = kaggle("datasets", "status", DATASET, check=False, capture=True)
    if exists.returncode == 0 and "ready" in (exists.stdout or "") + (exists.stderr or ""):
        kaggle("datasets", "version", "-p", PACK, "-m", msg, "--dir-mode", "zip")
    else:
        kaggle("datasets", "create", "-p", PACK, "--dir-mode", "zip")
    for _ in range(60):
        r = kaggle("datasets", "status", DATASET, check=False, capture=True)
        out = (r.stdout or "") + (r.stderr or "")
        print("  status:", out.strip()[-80:], flush=True)
        if "ready" in out:
            return
        time.sleep(20)
    raise SystemExit("Dataset chưa sẵn sàng sau 20 phút")


KERNEL_PY = '''# Sinh tự động bởi scripts/kaggle_job.py — đừng sửa tay.
import os, sys, shutil, subprocess, zipfile
from pathlib import Path
os.environ.update({env!r})
src = next(Path("/kaggle/input").rglob("PACK_MANIFEST.json")).parent
pack = Path("/kaggle/tmp/pack")
if pack.exists():
    shutil.rmtree(pack)
shutil.copytree(src, pack)
for z in list(pack.rglob("*.zip")):          # --dir-mode zip: thư mục con có thể là file .zip
    target = z.with_suffix("")
    with zipfile.ZipFile(z) as f:
        f.extractall(target if not any(n.startswith(target.name + "/") for n in f.namelist()) else z.parent)
    z.unlink()
os.environ["BIORERANK_PACK"] = str(pack)
code = pack / "code"
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-r", str(code / "requirements-kaggle.txt")], check=False)
sys.path.insert(0, str(code))
if shutil.which("nvidia-smi"):
    subprocess.run(["nvidia-smi", "-L"], check=False)
import importlib
importlib.import_module("src.kaggle_tasks.{task}").main()
'''


def push(task, smoke=False):
    gpu, ksrc, env = TASKS[task]
    env = {**env, "BIORERANK_SMOKE": "1" if smoke else "0"}
    d = KERNELS / task
    d.mkdir(parents=True, exist_ok=True)
    (d / "kernel.py").write_text(KERNEL_PY.format(env=env, task=TASK_MODULE.get(task, task)), encoding="utf-8")
    meta = {
        "id": f"{OWNER}/{slug(task)}", "title": slug(task), "code_file": "kernel.py", "language": "python",
        "kernel_type": "script", "is_private": True, "enable_gpu": gpu, "enable_internet": True,
        "dataset_sources": [DATASET], "competition_sources": [],
        "kernel_sources": [f"{OWNER}/{slug(k)}" for k in ksrc],
    }
    (d / "kernel-metadata.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    kaggle("kernels", "push", "-p", d)


def status(task):
    r = kaggle("kernels", "status", f"{OWNER}/{slug(task)}", check=False, capture=True)
    out = ((r.stdout or "") + (r.stderr or "")).lower()
    m = re.search(r'status "?([a-z_.]+)"?', out)
    return (m.group(1) if m else out.strip()[-60:]).replace("kernelworkerstatus.", "")


def wait(task, every=60, max_hours=11):
    t0 = time.time()
    while time.time() - t0 < max_hours * 3600:
        s = status(task)
        print(f"[{time.strftime('%H:%M:%S')}] {task}: {s}", flush=True)
        if s in ("complete", "error", "cancelacknowledged", "cancelrequested"):
            return s
        time.sleep(every)
    return "timeout"


def pull(task):
    dst = RESULTS / "kaggle" / task
    if dst.exists():
        shutil.rmtree(dst)
    dst.mkdir(parents=True)
    for attempt in range(5):                       # mạng chập chờn: thử lại
        r = kaggle("kernels", "output", f"{OWNER}/{slug(task)}", "-p", dst, check=False)
        if r.returncode == 0:
            break
        time.sleep(30 * (attempt + 1))
    else:
        raise SystemExit(f"Không tải được output của {task}")
    print("→", dst, flush=True)
    sync(task)


def sync(task):
    """Chép run TREC từ output Kaggle vào results/runs/<bộ>/<split>/ (nơi duy nhất mà bước đánh giá đọc)."""
    src = RESULTS / "kaggle" / task / "out" / "runs"
    n = 0
    for p in src.rglob("*.trec") if src.exists() else []:
        rel = p.relative_to(src)
        dst = RESULTS / "runs" / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(p, dst)
        n += 1
    print(f"đồng bộ {n} run → results/runs/", flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["upload", "push", "status", "wait", "pull", "all"])
    ap.add_argument("--task", choices=list(TASKS))
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("-m", "--message", default="update")
    a = ap.parse_args()
    if a.cmd == "upload":
        upload(a.message)
    elif a.cmd == "push":
        push(a.task, a.smoke)
    elif a.cmd == "status":
        print(status(a.task))
    elif a.cmd == "wait":
        print(wait(a.task))
    elif a.cmd == "pull":
        pull(a.task)
    elif a.cmd == "all":
        push(a.task, a.smoke)
        time.sleep(30)
        s = wait(a.task)
        pull(a.task)
        print("Kết thúc:", s)
        sys.exit(0 if s == "complete" else 1)
