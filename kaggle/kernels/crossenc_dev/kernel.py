# Sinh tự động bởi scripts/kaggle_job.py — đừng sửa tay.
import os, sys, shutil, subprocess, zipfile
from pathlib import Path
os.environ.update({'CE_SPLIT': 'dev', 'CE_E2': '0', 'BIORERANK_SMOKE': '0'})
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
importlib.import_module("src.kaggle_tasks.crossenc").main()
