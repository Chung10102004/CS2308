"""Đọc 3 bộ BEIR y sinh từ data/raw/beir/<bộ>/ (đã tải bằng `make data`)."""
import functools
import subprocess
from pathlib import Path

from ..utils.io import read_jsonl, read_qrels
from ..utils.paths import DATASETS, RAW

BEIR_URL = "https://public.ukp.informatik.tu-darmstadt.de/thakur/BEIR/datasets/{}.zip"


def download(root: Path = RAW / "beir"):
    root.mkdir(parents=True, exist_ok=True)
    for ds in DATASETS:
        if (root / ds / "corpus.jsonl").exists():
            continue
        z = root / f"{ds}.zip"
        subprocess.run(["curl", "-sSL", "-o", str(z), BEIR_URL.format(ds)], check=True)
        subprocess.run(["unzip", "-q", "-o", str(z), "-d", str(root)], check=True)


def ds_dir(ds: str) -> Path:
    assert ds in DATASETS, ds
    return RAW / "beir" / ds


@functools.lru_cache(maxsize=None)
def load_corpus(ds: str) -> dict:
    """docid -> {"title", "text"}."""
    return {r["_id"]: {"title": r.get("title") or "", "text": r.get("text") or ""}
            for r in read_jsonl(ds_dir(ds) / "corpus.jsonl")}


@functools.lru_cache(maxsize=None)
def load_queries(ds: str) -> dict:
    """qid -> văn bản truy vấn (trường `text` của BEIR; với TREC-COVID là `question`)."""
    return {r["_id"]: r["text"] for r in read_jsonl(ds_dir(ds) / "queries.jsonl")}


@functools.lru_cache(maxsize=None)
def load_qrels(ds: str, split: str = "test") -> dict:
    p = ds_dir(ds) / "qrels" / f"{split}.tsv"
    if not p.exists():
        return {}
    return read_qrels(p)


def doc_text(doc: dict) -> str:
    t, x = doc.get("title", ""), doc.get("text", "")
    return f"{t}. {x}".strip(". ").strip() if t else x
