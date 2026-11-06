"""Phân tích ngữ liệu (mục 4.7 của plan; mục 2 của tiểu luận) → results/data_report/corpus_stats.json + report/figures/fig_data_*.png

Chạy: python scripts/corpus_analysis.py   (cần `make data bm25 metadata` trước)
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.make_figures import BEIR3, C, DSN, save  # noqa: E402  (dùng chung style)
from src.data import metadata, scifact_open, trec_covid  # noqa: E402
from src.data.beir_loader import load_corpus, load_qrels, load_queries  # noqa: E402
from src.eval.ir_metrics import evaluate  # noqa: E402
from src.utils.io import read_run, write_json  # noqa: E402
from src.utils.paths import RESULTS, RUNS  # noqa: E402

TOKEN = re.compile(r"[a-z0-9]+(?:[-'][a-z0-9]+)*")
STOP = set("a an and are as at be by for from has have how in is it of on or that the this to was were what when "
           "which who why will with does do can".split())


def toks(s):
    return [t for t in TOKEN.findall(s.lower()) if t not in STOP]


def overlap(q, d):
    qt = set(toks(q))
    return len(qt & set(toks(d))) / max(len(qt), 1)


def stats():
    out = {}
    for ds in BEIR3:
        corpus, queries, qrels = load_corpus(ds), load_queries(ds), load_qrels(ds, "test")
        run = read_run(RUNS / ds / "test" / "bm25.trec")
        qlen = [len(TOKEN.findall(queries[q].lower())) for q in qrels]
        dlen = [len(TOKEN.findall((d["title"] + " " + d["text"]).lower())) for d in corpus.values()]
        rel = [sum(r > 0 for r in v.values()) for v in qrels.values()]
        levels = Counter(r for v in qrels.values() for r in v.values())
        ov_pos, ov_neg = [], []
        for q, docs in run.items():
            for d in docs:
                text = corpus[d]["title"] + " " + corpus[d]["text"]
                (ov_pos if qrels.get(q, {}).get(d, 0) > 0 else ov_neg).append(overlap(queries[q], text))
        m = evaluate(qrels, run)
        out[ds] = {
            "n_test_queries": len(qrels), "n_docs": len(corpus),
            "query_len_mean": float(np.mean(qlen)), "query_len_median": float(np.median(qlen)),
            "doc_len_mean": float(np.mean(dlen)), "doc_len_median": float(np.median(dlen)),
            "no_text_docs_pct": 100 * float(np.mean([not d["text"].strip() for d in corpus.values()])),
            "relevant_per_query_mean": float(np.mean(rel)), "relevant_per_query_median": float(np.median(rel)),
            "label_levels": {str(k): v for k, v in sorted(levels.items())},
            "bm25_recall@100": m["R@100"], "bm25_judged@10": m["Judged@10"],
            "bm25_judged@100": evaluate(qrels, run, [__import__("ir_measures").Judged @ 100])["Judged@100"],
            "queries_without_bm25_hits": len(set(qrels) - set(run)),
            "overlap_relevant_mean": float(np.mean(ov_pos)) if ov_pos else None,
            "overlap_nonrelevant_mean": float(np.mean(ov_neg)) if ov_neg else None,
            "_qlen": qlen, "_rel": rel, "_ov_pos": ov_pos, "_ov_neg": ov_neg,
        }
    so = scifact_open.report()
    per_claim = [(sum(e["provenance"] == "citation" for e in r["evidence"].values()),
                  sum(e["provenance"] == "pooling" for e in r["evidence"].values())) for r in scifact_open.claims().values()]
    out["scifact-open"] = {**so, "_per_claim": per_claim}
    out["trec-covid-rounds"] = trec_covid.rounds_report()
    dm = metadata.doc_meta()
    years = Counter(m["year"] for m in dm.values() if m.get("year"))
    pts = Counter(p for m in dm.values() for p in m.get("pub_types", []))
    mesh = Counter(x["descriptor"] for m in dm.values() for x in m.get("mesh", []) if x["major"])
    out["trec-covid-metadata"] = {"years": dict(sorted(years.items())), "top_pub_types": pts.most_common(12),
                                  "top_major_mesh": mesh.most_common(15)}
    return out


def figures(s):
    fig, axes = plt.subplots(1, 3, figsize=(13, 3.6))
    for ax, ds in zip(axes, BEIR3):
        v = s[ds]["_qlen"]
        ax.hist(v, bins=range(0, max(v) + 2), color=C["s1"], edgecolor=C["surface"], linewidth=1)
        ax.set_title(f"{DSN[ds]} — độ dài truy vấn")
        ax.set_xlabel("số token")
        ax.set_ylabel("số truy vấn")
    save(fig, "fig_data_query_length.png")

    fig, axes = plt.subplots(1, 3, figsize=(13, 3.6))
    for ax, ds in zip(axes, BEIR3):
        v = s[ds]["_rel"]
        ax.hist(v, bins=30, color=C["s1"], edgecolor=C["surface"], linewidth=1)
        ax.set_title(f"{DSN[ds]} — số bài đúng / truy vấn (TB {np.mean(v):.1f})")
        ax.set_xlabel("số bài đúng")
    save(fig, "fig_data_relevant_per_query.png")

    fig, ax = plt.subplots(figsize=(7, 3.8))
    x = np.arange(3)
    pos = [s[d]["overlap_relevant_mean"] for d in BEIR3]
    neg = [s[d]["overlap_nonrelevant_mean"] for d in BEIR3]
    ax.bar(x - 0.18, pos, 0.34, color=C["s1"], label="bài đúng trong BM25 top-100", edgecolor=C["surface"])
    ax.bar(x + 0.18, neg, 0.34, color=C["s2"], label="bài sai trong BM25 top-100", edgecolor=C["surface"])
    for xi, a, b in zip(x, pos, neg):
        ax.text(xi - 0.18, a + 0.01, f"{a:.2f}", ha="center", fontsize=8)
        ax.text(xi + 0.18, b + 0.01, f"{b:.2f}", ha="center", fontsize=8)
    ax.set_xticks(x, [DSN[d] for d in BEIR3])
    ax.set_ylabel("tỷ lệ từ của truy vấn có trong bài")
    ax.set_title("Độ trùng từ truy vấn – bài")
    ax.legend(loc="upper right")
    ax.set_ylim(0, 1)
    save(fig, "fig_data_lexical_overlap.png")

    pc = s["scifact-open"]["_per_claim"]
    fig, ax = plt.subplots(figsize=(6, 3.6))
    tot = Counter(c + p for c, p in pc)
    gain = Counter(p for c, p in pc if c + p > 0)
    ks = sorted(set(tot) | set(gain))
    ax.bar([k - 0.18 for k in ks], [tot.get(k, 0) for k in ks], 0.34, color=C["s1"], label="tổng bằng chứng / claim")
    ax.bar([k + 0.18 for k in ks], [gain.get(k, 0) for k in ks], 0.34, color=C["s2"], label="bằng chứng mới từ pooling / claim")
    ax.set_xlabel("số cặp bằng chứng")
    ax.set_ylabel("số claim")
    ax.set_title("SciFact-Open: 209 cặp gốc + 251 cặp tìm thêm")
    ax.legend()
    save(fig, "fig_data_scifact_open.png")


if __name__ == "__main__":
    s = stats()
    figures(s)
    write_json(RESULTS / "data_report" / "corpus_stats.json",
               {k: ({kk: vv for kk, vv in v.items() if not kk.startswith("_")} if isinstance(v, dict) else v) for k, v in s.items()})
    for ds in BEIR3:
        v = s[ds]
        print(f"{ds:11s} q_len {v['query_len_mean']:.1f}  d_len {v['doc_len_mean']:.0f}  rel/q {v['relevant_per_query_mean']:.1f}  "
              f"R@100 {v['bm25_recall@100']:.3f}  J@100 {v['bm25_judged@100']:.3f}  overlap+ {v['overlap_relevant_mean']:.2f} / - {v['overlap_nonrelevant_mean']:.2f}")
