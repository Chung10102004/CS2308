"""Đọc/ghi JSONL, YAML, run và qrels định dạng TREC."""
import gzip
import json
from collections import defaultdict
from pathlib import Path

import yaml

from .paths import CONFIGS


def _open(path, mode="rt"):
    path = Path(path)
    if path.suffix == ".gz":
        return gzip.open(path, mode, encoding=None if "b" in mode else "utf-8")
    return open(path, mode, encoding=None if "b" in mode else "utf-8")


def read_jsonl(path):
    with _open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


def write_jsonl(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with _open(path, "wt") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
            n += 1
    return n


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def load_yaml(name_or_path):
    p = Path(name_or_path)
    if not p.exists():
        p = CONFIGS / name_or_path
    return yaml.safe_load(p.read_text(encoding="utf-8"))


def read_qrels(path) -> dict:
    """qid -> {docid: rel}. Nhận cả TREC (4 cột) lẫn TSV của BEIR (có header)."""
    q = defaultdict(dict)
    with _open(path) as f:
        for line in f:
            parts = line.split()
            if not parts or parts[0] in ("query-id", "qid"):
                continue
            if len(parts) == 3:
                qid, did, rel = parts
            else:
                qid, _, did, rel = parts[:4]
            q[qid][did] = int(float(rel))
    return dict(q)


def write_qrels(path, qrels: dict, iteration="0"):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for qid in sorted(qrels, key=_natkey):
            for did, rel in sorted(qrels[qid].items()):
                f.write(f"{qid} {iteration} {did} {rel}\n")


def read_run(path) -> dict:
    """qid -> {docid: score}."""
    r = defaultdict(dict)
    with _open(path) as f:
        for line in f:
            parts = line.split()
            if len(parts) < 6:
                continue
            qid, _, did, _rank, score = parts[:5]
            r[qid][did] = float(score)
    return dict(r)


def write_run(path, run: dict, tag="run", depth=None):
    """run: qid -> {docid: score}. Ghi đã sắp xếp giảm dần theo điểm; hòa điểm giữ theo docid để tất định."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with _open(path, "wt") as f:
        for qid in sorted(run, key=_natkey):
            items = sorted(run[qid].items(), key=lambda x: (-x[1], x[0]))
            if depth:
                items = items[:depth]
            for rank, (did, s) in enumerate(items, 1):
                f.write(f"{qid} Q0 {did} {rank} {s:.6f} {tag}\n")


def ranking(run_q: dict) -> list:
    """Danh sách docid theo thứ tự điểm giảm dần."""
    return [d for d, _ in sorted(run_q.items(), key=lambda x: (-x[1], x[0]))]


def from_ranking(docids: list) -> dict:
    """Danh sách xếp hạng -> điểm giảm dần (n, n-1, …) để ghi run."""
    n = len(docids)
    return {d: float(n - i) for i, d in enumerate(docids)}


def _natkey(s):
    return (0, int(s)) if str(s).isdigit() else (1, str(s))
