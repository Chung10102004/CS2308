"""BM25 first-stage (R0): Pyserini, index BEIR "flat" dựng sẵn, lấy top-100 — đúng thiết lập RankGPT / Abdallah 2025.

Chạy: python -m src.retrieval.bm25            (mọi bộ, mọi split cần thiết)
Ra:   results/runs/<bộ>/<split>/bm25[.<biến thể>].trec
"""
import argparse
import json
import subprocess
from pathlib import Path

from ..data import scifact_open, splits, trec_covid
from ..data.beir_loader import load_queries
from ..utils.io import write_run
from ..utils.paths import DATA, RUNS, ensure_java

ensure_java()
DEPTH = 100
SO_INDEX = DATA / "indexes" / "scifact-open"
SO_COLLECTION = DATA / "processed" / "scifact_open_collection"


def searcher_for(ds: str):
    from pyserini.search.lucene import LuceneSearcher
    if ds == "scifact-open":
        if not SO_INDEX.exists():
            build_scifact_open_index()
        return LuceneSearcher(str(SO_INDEX))
    return LuceneSearcher.from_prebuilt_index(f"beir-v1.0.0-{ds}.flat")


def search(ds: str, queries: dict, k: int = DEPTH, threads: int = 16) -> dict:
    s = searcher_for(ds)
    qids = list(queries)
    hits = s.batch_search([queries[q] for q in qids], qids, k=k, threads=threads)
    return {q: {h.docid: float(h.score) for h in hits[q]} for q in qids}


def build_scifact_open_index(threads: int = 16):
    """Index Lucene cho kho 500K abstract của SciFact-Open (title + abstract, giống cách BEIR 'flat')."""
    SO_COLLECTION.mkdir(parents=True, exist_ok=True)
    out = SO_COLLECTION / "docs.jsonl"
    if not out.exists():
        with open(out, "w", encoding="utf-8") as f:
            for did, title, abstract in scifact_open.corpus_iter():
                f.write(json.dumps({"id": did, "contents": f"{title}\n{abstract}".strip()}, ensure_ascii=False) + "\n")
    SO_INDEX.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([
        "python", "-m", "pyserini.index.lucene", "--collection", "JsonCollection", "--input", str(SO_COLLECTION),
        "--index", str(SO_INDEX), "--generator", "DefaultLuceneDocumentGenerator", "--threads", str(threads),
        "--storeRaw"], check=True)


def run_path(ds: str, split: str, system: str, variant: str | None = None) -> Path:
    name = system if not variant else f"{system}.{variant}"
    return RUNS / ds / split / f"{name}.trec"


def main(only=None):
    sp = splits.load()
    jobs = []
    for ds in ("trec-covid", "nfcorpus", "scifact"):
        q = load_queries(ds)
        for split, qids in sp[ds].items():
            jobs.append((ds, split, None, {i: q[i] for i in qids}))
    for v, qs in trec_covid.query_variants().items():
        if v != "Q-q":
            jobs.append(("trec-covid", "test", v, qs))
    so = scifact_open.queries()
    jobs.append(("scifact-open", "test", None, {i: so[i] for i in sp["scifact-open"]["test"]}))
    for ds, split, variant, qs in jobs:
        if only and ds not in only:
            continue
        run = search(ds, qs)
        p = run_path(ds, split, "bm25", variant)
        write_run(p, run, tag="bm25")
        print(f"{ds:13s} {split:5s} {variant or '':5s} {len(run):5d} truy vấn → {p.relative_to(RUNS.parent)}", flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="*")
    main(ap.parse_args().only)
