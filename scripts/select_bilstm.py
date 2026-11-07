"""Chọn biến thể BiLSTM-ESIM v2 theo dev nDCG@10 (trung bình điểm dev tốt nhất qua 3 seed) → results/bilstm_selection.json.
Chỉ xét biến thể có đủ 3 seed. v1 là mốc so sánh, không nằm trong tập chọn của v2."""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.utils.paths import RESULTS  # noqa: E402

VARIANTS = {
    "bilstm2": "BiLSTM-ESIM v2 (à la carte + khớp từ)",
    "bilstm2_noem": "BiLSTM-ESIM v2 (à la carte, không khớp từ)",
    "bilstm2_nooov": "BiLSTM-ESIM v2 (khớp từ, không à la carte)",
}


def logs(tag):
    return sorted((RESULTS / "kaggle").glob(f"*/out/train_log_{tag}_s?.json"))


def main():
    rows = {}
    for tag in VARIANTS:
        v = {json.loads(p.read_text())["seed"]: json.loads(p.read_text())["best_dev_ndcg10"] for p in logs(tag)}
        rows[tag] = {"seeds": v, "mean": float(np.mean(list(v.values()))) if v else None}
    ok = {t: r for t, r in rows.items() if len(r["seeds"]) == 3}
    v1 = [json.loads(p.read_text())["best_dev_ndcg10"] for p in sorted((RESULTS / "kaggle" / "bilstm" / "out").glob("train_log_s?.json"))]
    if not ok:
        print("Chưa có biến thể v2 nào đủ 3 seed.")
        return
    chosen = max(ok, key=lambda t: ok[t]["mean"])
    out = {"chosen": chosen, "label": VARIANTS[chosen], "variants": rows, "v1_dev_mean": float(np.mean(v1)) if v1 else None,
           "rule": "trung bình dev nDCG@10 tốt nhất qua 3 seed (NFCorpus dev + SciFact dev); dev không có TREC-COVID"}
    (RESULTS / "bilstm_selection.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
    print("chọn:", chosen, {t: (round(r["mean"], 4) if r["mean"] else None, len(r["seeds"])) for t, r in rows.items()})


if __name__ == "__main__":
    main()
