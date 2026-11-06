"""Đường dẫn dùng chung. Mọi module lấy đường dẫn từ đây, không tự ghép chuỗi."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = Path(os.environ.get("BIORERANK_DATA", ROOT / "data"))
RAW = DATA / "raw"
PROC = DATA / "processed"
CAND = DATA / "candidates"
PACK = DATA / "kaggle_pack"
CACHE = DATA / "cache"
RESULTS = Path(os.environ.get("BIORERANK_RESULTS", ROOT / "results"))
RUNS = RESULTS / "runs"
CONFIGS = ROOT / "configs"
REPORT = ROOT / "report"

DATASETS = ("trec-covid", "nfcorpus", "scifact")

JAVA_HOME_DEFAULT = "/usr/lib/jvm/java-21-openjdk-amd64"


def ensure_java():
    """Pyserini cần JAVA_HOME; đặt mặc định nếu chưa có."""
    if "JAVA_HOME" not in os.environ and Path(JAVA_HOME_DEFAULT).exists():
        os.environ["JAVA_HOME"] = JAVA_HOME_DEFAULT
