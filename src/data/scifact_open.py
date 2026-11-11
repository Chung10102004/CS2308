"""SciFact-Open (Wadden et al., 2022): 279 claim, kho 500K abstract, nhãn gốc và nhãn sau khi gom pool.

claims.jsonl: evidence[doc_id] = {"provenance": "citation"|"pooling", "label", "sentences", "model_ranks"}
- qrels_orig = các cặp provenance == "citation" (nhãn gốc của SciFact)
- qrels_open = toàn bộ cặp (nhãn đã được chuyên gia soát lại)
"""
import functools
import subprocess

from ..utils.io import read_jsonl
from ..utils.paths import RAW

URL = "https://scifact.s3.us-west-2.amazonaws.com/scifact-open/latest/scifact_open.tar.gz"
ROOT = RAW / "scifact_open"


def download():
    if (ROOT / "data" / "claims.jsonl").exists():
        return
    ROOT.mkdir(parents=True, exist_ok=True)
    tgz = ROOT / "scifact_open.tar.gz"
    subprocess.run(["curl", "-sSL", "-o", str(tgz), URL], check=True)
    subprocess.run(["tar", "-xzf", str(tgz), "-C", str(ROOT)], check=True)


@functools.lru_cache(maxsize=None)
def claims() -> dict:
    return {str(r["id"]): r for r in read_jsonl(ROOT / "data" / "claims.jsonl")}


def queries() -> dict:
    return {qid: r["claim"] for qid, r in claims().items()}


def qrels(kind: str = "open") -> dict:
    if kind not in ("orig", "open"):
        raise ValueError(f"kind phải là 'orig' hoặc 'open', nhận {kind!r}")
    out = {}
    for qid, r in claims().items():
        ev = {str(d): 1 for d, e in r["evidence"].items() if kind == "open" or e["provenance"] == "citation"}
        if ev:
            out[qid] = ev
    return out


def corpus_iter():
    """Sinh (docid, title, abstract) cho 500K bài; abstract là danh sách câu."""
    for r in read_jsonl(ROOT / "data" / "corpus.jsonl"):
        yield str(r["doc_id"]), r.get("title") or "", " ".join(r.get("abstract") or [])


def report() -> dict:
    c = claims()
    n_cit = sum(e["provenance"] == "citation" for r in c.values() for e in r["evidence"].values())
    n_pool = sum(e["provenance"] == "pooling" for r in c.values() for e in r["evidence"].values())
    qo, qn = qrels("orig"), qrels("open")
    return {
        "n_claims": len(c),
        "evidence_citation": n_cit,
        "evidence_pooling": n_pool,
        "evidence_total": n_cit + n_pool,
        "claims_with_evidence_orig": len(qo),
        "claims_with_evidence_open": len(qn),
        "claims_in_both": len(set(qo) & set(qn)),
        "claims_gaining_evidence": sum(len(qn[q]) > len(qo.get(q, {})) for q in qn),
        "note_negatives": "repo không phát hành cặp đã chấm nhưng không phải bằng chứng (chỉ có claims/corpus/retrievals/predictions)",
    }
