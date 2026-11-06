"""Tiện ích dùng chung cho các task chạy trên Kaggle (cũng chạy được local để thử với SMOKE=1)."""
import json
import math
import os
import time
from collections import defaultdict
from pathlib import Path

SMOKE = os.environ.get("BIORERANK_SMOKE", "0") == "1"
ON_KAGGLE = Path("/kaggle/working").exists()


def find_pack() -> Path:
    env = os.environ.get("BIORERANK_PACK")
    if env:
        return Path(env)
    roots = [Path("/kaggle/input")] if ON_KAGGLE else [Path(__file__).resolve().parents[2] / "data" / "kaggle_pack"]
    for r in roots:
        if (r / "PACK_MANIFEST.json").exists():
            return r
        for p in sorted(r.rglob("PACK_MANIFEST.json")):
            return p.parent
    raise FileNotFoundError("Không tìm thấy PACK_MANIFEST.json trong " + ", ".join(map(str, roots)))


def out_dir(task: str) -> Path:
    base = Path("/kaggle/working/out") if ON_KAGGLE else Path(__file__).resolve().parents[2] / "results" / "kaggle_local" / task
    base.mkdir(parents=True, exist_ok=True)
    return base


def read_jsonl(p):
    with open(p, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


class Pack:
    def __init__(self, root: Path | None = None):
        self.root = root or find_pack()
        self.manifest = json.loads((self.root / "PACK_MANIFEST.json").read_text())
        self._corpus = {}

    def corpus(self, ds) -> dict:
        if ds not in self._corpus:
            self._corpus[ds] = {d["docid"]: d for d in read_jsonl(self.root / "corpus" / f"{ds}.jsonl")}
        return self._corpus[ds]

    def queries(self, ds, split, variant="Q-q") -> dict:
        p = self.root / "queries" / f"{ds}__{split}__{variant}.jsonl"
        q = {r["qid"]: r["text"] for r in read_jsonl(p)}
        return dict(list(q.items())[:3]) if SMOKE else q

    def run(self, ds, split) -> dict:
        """qid -> [(docid, bm25)] theo thứ tự BM25."""
        r = defaultdict(list)
        with open(self.root / "runs" / f"{ds}__{split}.trec") as f:
            for line in f:
                qid, _, did, rank, score, _ = line.split()
                r[qid].append((did, float(score)))
        return dict(r)

    def qrels(self, ds, split) -> dict:
        q = defaultdict(dict)
        p = self.root / "qrels" / f"{ds}__{split}.tsv"
        if p.exists():
            for line in open(p):
                qid, did, rel = line.split("\t")
                q[qid][did] = int(rel)
        return dict(q)


def doc_text(doc: dict, with_meta: bool = False) -> str:
    t = (doc.get("title") or "").strip()
    x = (doc.get("text") or "").strip()
    s = f"{t}. {x}" if t else x
    if with_meta and doc.get("meta"):
        s = f"{doc['meta']} {s}"
    return s


def write_run(path: Path, run: dict, tag: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        for qid, scores in run.items():
            for rank, (did, s) in enumerate(sorted(scores.items(), key=lambda x: (-x[1], x[0])), 1):
                f.write(f"{qid} Q0 {did} {rank} {s:.6f} {tag}\n")


def ndcg10(qrels: dict, run: dict) -> float:
    """nDCG@10 (gain tuyến tính như trec_eval) — chỉ dùng để early stopping trên dev."""
    tot, n = 0.0, 0
    for qid, rel in qrels.items():
        if not any(v > 0 for v in rel.values()):
            continue
        n += 1
        ranked = sorted(run.get(qid, {}).items(), key=lambda x: -x[1])[:10]
        dcg = sum(rel.get(d, 0) / math.log2(i + 2) for i, (d, _) in enumerate(ranked))
        ideal = sorted((v for v in rel.values() if v > 0), reverse=True)[:10]
        idcg = sum(v / math.log2(i + 2) for i, v in enumerate(ideal))
        tot += dcg / idcg if idcg else 0
    return tot / max(n, 1)


def gpu_name() -> str:
    try:
        import torch
        return torch.cuda.get_device_name(0) if torch.cuda.is_available() else "cpu"
    except Exception:
        return "cpu"


class Timer:
    def __enter__(self):
        self.t = time.perf_counter()
        return self

    def __exit__(self, *a):
        self.ms = (time.perf_counter() - self.t) * 1000


# Ứng viên dùng chung: run BM25 Q-q; biến thể truy vấn chỉ đổi văn bản truy vấn đưa vào reranker (E2)
TEST_SETS = [("trec-covid", "test"), ("nfcorpus", "test"), ("scifact", "test"), ("scifact-open", "test")]
E2_VARIANTS = [("Q-kw", False), ("Q-qn", False), ("Q-q", True), ("Q-kw", True), ("Q-qn", True)]


def run_name(model: str, variant: str = "Q-q", meta: bool = False) -> str:
    s = model
    if variant != "Q-q":
        s += f".{variant}"
    if meta:
        s += ".M1"
    return s
