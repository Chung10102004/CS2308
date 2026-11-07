"""RRF ensemble (Cormack et al., 2009), tổ hợp CHỌN TRÊN DEV, áp một lần lên test.

- Ứng viên: chỉ các hệ thống zero-shot (BM25, cross-encoder, Qwen3) — dev của chúng không bị dùng để huấn luyện.
  Không đưa LambdaMART/BiLSTM vào vì dev đã dùng để early stopping (điểm dev bị lạc quan).
- Chọn: forward selection tham lam theo nDCG@10 trung bình trên NFCorpus dev + SciFact dev, RRF k = 60,
  dừng khi không tăng thêm ≥ 0,001.
- TREC-COVID không có dev: dùng nguyên tổ hợp đã chọn (zero-shot).
Ra: results/runs/<bộ>/test/rrf_dev.trec, results/ensemble.json
"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.eval.ir_metrics import evaluate  # noqa: E402
from src.rerank.candidates import pack  # noqa: E402
from src.utils.io import read_run, write_json, write_run  # noqa: E402
from src.utils.paths import RESULTS, RUNS  # noqa: E402

CANDIDATES = ["bm25", "medcpt_ce", "bge_v2_m3", "bge_base", "bge_large", "mxbai_base", "monot5_base", "qwen3_4b"]
DEV = [("nfcorpus", "dev"), ("scifact", "dev")]
TEST = ["trec-covid", "nfcorpus", "scifact", "scifact-open"]
K, MIN_GAIN, NAME = 60, 1e-3, "rrf_dev"


def rrf(runs, k=K):
    out = {}
    for r in runs:
        for q, docs in r.items():
            for rank, (d, _) in enumerate(sorted(docs.items(), key=lambda x: (-x[1], x[0])), 1):
                out.setdefault(q, {})[d] = out.get(q, {}).get(d, 0.0) + 1.0 / (k + rank)
    return out


def dev_score(members, dev_runs, dev_qrels):
    return float(np.mean([evaluate(dev_qrels[s], rrf([dev_runs[m][s] for m in members]))["nDCG@10"] for s in DEV]))


def main():
    P = pack()
    dev_qrels = {s: P.qrels(*s) for s in DEV}
    dev_runs = {}
    for m in CANDIDATES:
        paths = {s: RUNS / s[0] / s[1] / f"{m}.trec" for s in DEV}
        if all(p.exists() for p in paths.values()):
            dev_runs[m] = {s: read_run(p) for s, p in paths.items()}
    avail = list(dev_runs)
    if not avail:
        raise SystemExit("Chưa có run dev của hệ thống nào (chạy task Kaggle crossenc_dev/qwen3 trước).")
    singles = {m: dev_score([m], dev_runs, dev_qrels) for m in avail}
    chosen = [max(singles, key=singles.get)]
    best, trace = singles[chosen[0]], [{"members": list(chosen), "dev_ndcg10": singles[chosen[0]]}]
    while True:
        cand = {m: dev_score(chosen + [m], dev_runs, dev_qrels) for m in avail if m not in chosen}
        if not cand:
            break
        m, sc = max(cand.items(), key=lambda x: x[1])
        if sc < best + MIN_GAIN:
            break
        chosen.append(m)
        best = sc
        trace.append({"members": list(chosen), "dev_ndcg10": sc})
    test = {}
    for ds in TEST:
        paths = [RUNS / ds / "test" / f"{m}.trec" for m in chosen]
        if all(p.exists() for p in paths):
            write_run(RUNS / ds / "test" / f"{NAME}.trec", rrf([read_run(p) for p in paths]), NAME)
            test[ds] = True
    rep = {"candidates_available": avail, "single_dev_ndcg10": singles, "chosen": chosen, "dev_ndcg10": best,
           "selection_trace": trace, "k": K, "written_test": test,
           "note": "chọn hoàn toàn trên dev (NFCorpus dev + SciFact dev); TREC-COVID dùng zero-shot"}
    write_json(RESULTS / "ensemble.json", rep)
    print("chọn:", chosen, "dev nDCG@10 =", round(best, 4))
    print("đơn lẻ:", {k: round(v, 4) for k, v in sorted(singles.items(), key=lambda x: -x[1])})


if __name__ == "__main__":
    main()
