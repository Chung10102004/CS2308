"""Metric truy xuất. nDCG@10 tính bằng ir_measures (pytrec_eval) với nhãn nhiều mức giữ nguyên — như BEIR."""
import ir_measures
from ir_measures import P, R, RR, Judged, nDCG

MAIN = [nDCG @ 10, RR @ 10, R @ 10, R @ 100, Judged @ 10]


def _q(qrels):
    return {q: {d: int(r) for d, r in v.items()} for q, v in qrels.items()}


def evaluate(qrels: dict, run: dict, measures=MAIN, restrict_to=None) -> dict:
    """Trung bình trên các truy vấn có trong qrels (truy vấn thiếu trong run tính 0, như pytrec_eval của BEIR)."""
    qrels = _q(qrels)
    if restrict_to is not None:
        keep = set(restrict_to)
        qrels = {q: v for q, v in qrels.items() if q in keep}
    run = {q: v for q, v in run.items() if q in qrels}
    agg = ir_measures.calc_aggregate(measures, qrels, run)
    return {str(m): float(v) for m, v in agg.items()}


def per_query(qrels: dict, run: dict, measure=nDCG @ 10) -> dict:
    qrels = _q(qrels)
    out = {q: 0.0 for q in qrels}
    for m in ir_measures.iter_calc([measure], qrels, {q: v for q, v in run.items() if q in qrels}):
        out[m.query_id] = float(m.value)
    return out


def judged_at(qrels: dict, run: dict, k: int = 10) -> float:
    return evaluate(qrels, run, [Judged @ k])[f"Judged@{k}"]
