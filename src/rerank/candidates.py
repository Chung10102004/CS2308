"""Lấy ứng viên (BM25 top-100 cố định) kèm văn bản để đưa vào reranker local/API — dùng chung với gói Kaggle."""
import random

from ..kaggle_tasks.common import Pack, doc_text
from ..utils.io import ranking, read_run
from ..utils.paths import PACK, RUNS

_PACK = None


def pack() -> Pack:
    global _PACK
    if _PACK is None:
        _PACK = Pack(PACK)
    return _PACK


def items(ds, split="test", variant="Q-q", meta=False, depth=100, order_from=None, shuffle_seed=None, limit=None):
    """[(qid, query_text, docids, texts)]. order_from = tên run để lấy thứ tự ứng viên (mặc định BM25)."""
    p = pack()
    queries = p.queries(ds, split, variant)
    if order_from:
        base = {q: ranking(v) for q, v in read_run(RUNS / ds / split / f"{order_from}.trec").items()}
    else:
        base = {q: [d for d, _ in v] for q, v in p.run(ds, split).items()}
    corpus = p.corpus(ds)
    out = []
    for qid in list(queries)[:limit] if limit else queries:
        dids = base.get(qid, [])[:depth]
        if shuffle_seed is not None:
            dids = dids[:]
            random.Random(f"{shuffle_seed}-{qid}").shuffle(dids)
        out.append((qid, queries[qid], dids, [doc_text(corpus[d], with_meta=meta) for d in dids]))
    return out


def narratives() -> dict:
    return pack().queries("trec-covid", "test", "narrative")
