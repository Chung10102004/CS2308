"""Sinh bảng Markdown cho tiểu luận/slide từ results/e*/ và src/eval/published.py → report/tables/*.md.
Mọi con số trong bảng truy được về file kết quả hoặc về bảng của bài báo (cột Nguồn)."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.eval import published as PUB  # noqa: E402
from src.eval.systems import BY_ID, SYSTEMS  # noqa: E402
from src.utils.paths import REPORT, RESULTS  # noqa: E402

T = REPORT / "tables"
BEIR3 = ("trec-covid", "nfcorpus", "scifact")
DSN = {"trec-covid": "TREC-COVID", "nfcorpus": "NFCorpus", "scifact": "SciFact", "scifact-open": "SciFact-Open"}
DASH = "—"


def load(p):
    p = RESULTS / p
    return json.loads(p.read_text()) if p.exists() else None


def f100(x, sd=None, nd=2):
    if x is None:
        return DASH
    s = f"{100 * x:.{nd}f}"
    return s + (f" ± {100 * sd:.{nd}f}" if sd else "")


def write(name, text):
    T.mkdir(parents=True, exist_ok=True)
    (T / name).write_text(text.strip() + "\n", encoding="utf-8")
    print("→", T / name)


def table_e0():
    rows = load("e0/e0.json") or []
    out = ["| Hệ thống | Bộ | Nhóm chạy lại | Bài báo | Lệch | Ngưỡng | Đạt? |", "|---|---|---:|---:|---:|---:|:---:|"]
    for r in rows:
        ok = DASH if r.get("ours") is None else ("✓" if r["pass"] else "✗")
        out.append(f"| {r['label']} | {DSN[r['ds']]} | {r['ours'] if r.get('ours') is not None else DASH} | {r['paper']} | "
                   f"{r.get('diff', DASH)} | ±{r.get('tol', DASH)} | {ok} |")
    out.append("\nnDCG@10 × 100. Bài báo: " + PUB.ABDALLAH + ". BM25 NFCorpus của Pyserini 2CR là 32,2 (≠ 30,75 trong bài) — xem mục 10.3 của plan.")
    write("e0_reproduction.md", "\n".join(out))


def table_e1():
    e1 = load("e1/e1.json") or {}
    head = "| | Hệ thống | Thế hệ | " + " | ".join(DSN[d] for d in BEIR3) + " | TB |"
    out = [head, "|---|---|---|" + "---:|" * 4]
    for name, gen, year, sc, src, note in PUB.ABDALLAH_ROWS:
        vals = [sc[d] for d in BEIR3]
        out.append(f"| công bố | {name} | {gen} | " + " | ".join(f"{v:.2f}" for v in vals) + f" | {sum(vals) / 3:.2f} |")
    for s in SYSTEMS:
        cells, vals = [], []
        for d in BEIR3:
            m = (e1.get(d) or {}).get(s.sid)
            if not m:
                cells.append(DASH)
                continue
            mark = ""
            if m.get("vs_R0", {}).get("sig") and m["vs_R0"]["delta"] > 0:
                mark += "†"
            if m.get("vs_R4", {}).get("sig"):
                mark += "‡" if m["vs_R4"]["delta"] > 0 else "▾"
            cells.append(f"**{f100(m['nDCG@10'], m.get('nDCG@10_sd'))}**{mark}")
            vals.append(m["nDCG@10"])
        avg = f"**{100 * sum(vals) / 3:.2f}**" if len(vals) == 3 else DASH
        out.append(f"| **nhóm** {s.sid} | **{s.label}** | {s.gen} | " + " | ".join(cells) + f" | {avg} |")
    out.append("\nnDCG@10 × 100, cùng BM25 (Pyserini flat) top-100. Dòng *công bố*: " + PUB.ABDALLAH +
               " (bảng 2–3). Dòng **nhóm**: số của nhóm; nhiều seed thì ghi trung bình ± SD (3 seed). "
               "† hơn BM25, ‡ hơn bge-reranker-v2-m3, ▾ kém bge-reranker-v2-m3 — paired bootstrap 10.000 lần, hiệu chỉnh Holm, p < 0,05. "
               "RankGPT gpt-4 và GPT-6.1 Sol của nhóm chỉ xếp lại top-30 của model nhỏ.")
    write("e1_main.md", "\n".join(out))
    out = ["| Hệ thống | Bộ | nDCG@10 | KTC 95% | MRR@10 | R@10 | R@100 | Judged@10 |", "|---|---|---:|---|---:|---:|---:|---:|"]
    for s in SYSTEMS:
        for d in BEIR3:
            m = (e1.get(d) or {}).get(s.sid)
            if m:
                ci = m["ci95"][1]
                out.append(f"| {s.sid} {s.label} | {DSN[d]} | {f100(m['nDCG@10'])} | "
                           f"{f100(ci[0])}–{f100(ci[1])} | {f100(m['RR@10'])} | {f100(m['R@10'])} | {f100(m['R@100'])} | {f100(m['Judged@10'], nd=1)} |")
    write("e1_full.md", "\n".join(out))


def table_e2():
    e2 = load("e2/e2.json")
    if not e2:
        return
    cols = ["Q-q", "Q-kw", "Q-qn", "Q-q+M1", "Q-kw+M1", "Q-qn+M1"]
    out = ["| Hệ thống | " + " | ".join(cols) + " |", "|---|" + "---:|" * len(cols)]
    bm = e2["bm25_first_stage"]
    out.append("| R0 BM25 (first-stage, truy vấn đổi) | " + " | ".join(f100(bm.get(c)) if "+" not in c else DASH for c in cols) + " |")
    for sid, row in e2["variants"].items():
        out.append(f"| {sid} {BY_ID[sid].label} | " + " | ".join(f100((row.get(c) or {}).get("nDCG@10")) for c in cols) + " |")
    lm = e2.get("lambdamart_cv", {})
    out.append(f"| R1 LambdaMART (CV 5-fold trên TREC-COVID) | {f100((lm.get('M0') or {}).get('nDCG@10'))} | {DASH} | {DASH} | "
               f"{f100((lm.get('M1') or {}).get('nDCG@10'))} | {DASH} | {DASH} |")
    out.append("\nTREC-COVID, nDCG@10 × 100. Q-kw = trường `query` (từ khóa), Q-q = `question` (mặc định BEIR), "
               "Q-qn = question + narrative; +M1 = chèn dòng metadata (journal, năm, loại bài, MeSH) trước abstract. "
               "Ứng viên giữ cố định (BM25 Q-q top-100), chỉ đổi thứ đưa vào reranker; riêng dòng R0 là BM25 chạy lại với truy vấn đổi.")
    parts = ["\n".join(out)]
    o = ["| Hệ thống | Bộ | Tiêu chí chung | Tiêu chí y khoa / narrative | Δ | p |", "|---|---|---:|---:|---:|---:|"]
    for sid, by in e2["criteria"].items():
        for d, v in by.items():
            t = v.get("test") or {}
            o.append(f"| {sid} | {DSN[d]} | {f100(v.get('generic'))} | {f100(v.get('domain'))} | "
                     f"{f100(t.get('delta')) if t else DASH} | {('%.3f' % t['p']) if t else DASH} |")
    parts.append("### Tiêu chí 2×2 (Jev, GPT)\n" + "\n".join(o))
    o = ["| Bộ | Jev listwise | Jev pointwise |", "|---|---:|---:|"]
    for d, v in e2["listwise_vs_pointwise"].items():
        o.append(f"| {DSN[d]} | {f100(v['listwise'])} | {f100(v['pointwise'])} |")
    parts.append("### Jev listwise và pointwise\n" + "\n".join(o))
    o = ["| Hệ thống | Bộ | τ TB (xáo so với gốc) | nDCG@10 gốc | Biên độ nDCG@10 qua 4 lần |", "|---|---|---:|---:|---:|"]
    for name, by in e2["position_bias"].items():
        for d, v in by.items():
            o.append(f"| {name} | {DSN[d]} | {('%.3f' % v['mean_tau_vs_original']) if v else DASH} | "
                     f"{f100(v['ndcg10_original']) if v else DASH} | {f100(v['ndcg10_range']) if v else DASH} |")
    parts.append("### Thiên vị vị trí (xáo thứ tự ứng viên 3 lần)\n" + "\n".join(o))
    o = ["| Hệ thống | Gốc | + λ·MeSH (CV) | Δ | p | λ theo fold |", "|---|---:|---:|---:|---:|---|"]
    for sid, v in (e2.get("mesh_boost") or {}).items():
        o.append(f"| {sid} {BY_ID[sid].label} | {f100(v['base'])} | {f100(v['boosted_cv'])} | {f100(v['delta'])} | "
                 f"{v['test']['p']:.3f} | {', '.join(str(x) for x in v['lambdas'])} |")
    parts.append("### Boost hậu kỳ theo độ trùng MeSH (TREC-COVID, λ chọn bằng CV 5-fold)\n" + "\n".join(o))
    write("e2_metadata.md", "\n\n".join(parts))


def table_e3():
    e3 = load("e3/e3.json")
    if not e3:
        return
    parts = []
    for scope in ("intersection", "all"):
        so = e3["scifact_open"][scope]
        o = ["| Hệ thống | nDCG@10 nhãn gốc | nDCG@10 nhãn đã soát | Δ | R@10 gốc | R@10 soát | Hạng gốc → soát |",
             "|---|---:|---:|---:|---:|---:|:---:|"]
        k = so.get("kendall") or {}
        for sid, v in sorted(so["systems"].items(), key=lambda x: -x[1]["open"]):
            rk = f"{k['rank_a'][sid]} → {k['rank_b'][sid]}" if k else DASH
            o.append(f"| {sid} {BY_ID[sid].label} | {f100(v['orig'])} | {f100(v['open'])} | {f100(v['delta'])} | "
                     f"{f100(v['R@10_orig'])} | {f100(v['R@10_open'])} | {rk} |")
        tau = f"Kendall τ = {k['tau']:.3f}, {k['swapped_pairs']} cặp hệ thống đổi thứ tự / {k['n_systems']} hệ thống" if k else ""
        title = "giao 190 claim có bằng chứng ở cả hai bộ nhãn" if scope == "intersection" else "toàn bộ claim hợp lệ của từng bộ nhãn"
        parts.append(f"### SciFact-Open — {title}\n" + "\n".join(o) + f"\n\n{tau}\n\nKhông báo Judged@10: repo SciFact-Open không phát hành các cặp đã chấm là không liên quan.")
    lv = e3["trec_covid_rounds"]["levels"]
    o = ["| Nhãn tới hết vòng | Số cặp có nhãn | τ (nDCG@10) | τ (condensed) | Cặp đổi thứ tự |", "|---|---:|---:|---:|---:|"]
    for l, v in lv.items():
        k, kc = v.get("kendall") or {}, v.get("kendall_condensed") or {}
        o.append(f"| {l} | {v['n_pairs']} | {('%.3f' % k['tau']) if k else DASH} | {('%.3f' % kc['tau']) if kc else DASH} | "
                 f"{k.get('swapped_pairs', DASH)} |")
    parts.append(f"### TREC-COVID — nhãn theo vòng so với nhãn đầy đủ ({e3['trec_covid_rounds']['n_topics']} topic)\n" + "\n".join(o))
    write("e3_labels.md", "\n\n".join(parts))


def table_e4():
    e4 = load("e4/e4.json")
    if not e4:
        return
    o = ["| Hệ thống | Loại | p50 (ms/truy vấn) | p95 | p99 | USD / 1.000 truy vấn | nDCG@10 TB 3 bộ |", "|---|---|---:|---:|---:|---:|---:|"]
    for sid, v in sorted(e4.items(), key=lambda x: x[1].get("usd_per_1k") or 0):
        def ms(k):
            return f"{v[k]:.0f}" if v.get(k) is not None else DASH
        o.append(f"| {sid} {BY_ID[sid].label if sid in BY_ID else ''} | {v['kind']} | {ms('p50_ms')} | {ms('p95_ms')} | {ms('p99_ms')} | "
                 f"{v['usd_per_1k']:.4f} | {f100(v.get('mean_ndcg10_beir3'))} |")
    o.append("\nLocal: Tesla T4 trên Kaggle, mỗi truy vấn 100 ứng viên, quy USD theo giá thuê T4 trong configs/pricing.yaml (ước lượng). "
             "API: tổng chi phí thật từ log / số truy vấn; độ trễ là tổng các lệnh gọi tuần tự của một truy vấn.")
    write("e4_cost.md", "\n".join(o))


def table_data():
    sp = load("data_report/splits.json") or {}
    cov = load("data_report/trec_covid_metadata_coverage.json") or {}
    e3 = load("e3/e3.json") or {}
    o = ["| Bộ | Train | Dev | Test |", "|---|---:|---:|---:|"]
    for ds, v in (sp.get("sizes") or {}).items():
        o.append(f"| {DSN[ds]} | {v.get('train', DASH)} | {v.get('dev', DASH)} | {v.get('test', DASH)} |")
    o.append(f"\nLoại {sp.get('dropped_from_train', DASH)} câu train gần trùng (TF-IDF cosine > 0,9) với câu test.")
    if cov:
        o.append(f"\nMetadata TREC-COVID ({cov['n_docs']} bài ứng viên): PMID {cov['pct_has_pubmed_id']}%, MeSH {cov['pct_has_mesh']}%, "
                 f"loại bài {cov['pct_has_pub_types']}%, tạp chí {cov['pct_has_journal']}%, năm {cov['pct_has_year']}%.")
    rep = (e3.get("trec_covid_rounds") or {}).get("report")
    if rep:
        o.append(f"\nTREC-COVID: {rep['n_judgments']} nhãn NIST; vòng 1 có {rep['n_topics_round1']} topic; "
                 f"nhãn vòng 1 trên các topic đó: {rep['shallow_pairs']} cặp ({rep['shallow_relevant']} liên quan) so với "
                 f"{rep['full_pairs_round1_topics']} cặp ({rep['full_relevant_round1_topics']} liên quan) ở bản đầy đủ.")
    write("data_overview.md", "\n".join(o))


if __name__ == "__main__":
    table_data()
    table_e0()
    table_e1()
    table_e2()
    table_e3()
    table_e4()
