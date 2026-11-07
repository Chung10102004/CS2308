"""Chấm mọi run đang có và ghi kết quả E0–E4 vào results/e*/ (bảng và hình đọc từ đây).

  python scripts/run_experiment.py            # tất cả
  python scripts/run_experiment.py --only e1 e3
Hệ thống chưa có run (ví dụ R5/R6 khi chưa điền API key) được ghi là thiếu, không làm hỏng các phần khác.
"""
import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.data import metadata, scifact_open, trec_covid  # noqa: E402
from src.data.beir_loader import load_qrels  # noqa: E402
from src.eval import published as PUB  # noqa: E402
from src.eval.ir_metrics import evaluate, per_query  # noqa: E402
from src.eval.rank_correlation import kendall  # noqa: E402
from src.eval.significance import holm, mean_ci, paired_bootstrap  # noqa: E402
from src.eval.systems import BY_ID, SYSTEMS, load_runs  # noqa: E402
from src.utils.io import load_yaml, read_jsonl, read_run, write_json  # noqa: E402
from src.utils.paths import RESULTS, RUNS  # noqa: E402

BEIR3 = ("trec-covid", "nfcorpus", "scifact")
MAIN_IDS = [s.sid for s in SYSTEMS if s.main]


def qrels_for(ds):
    return load_qrels(ds, "test")


def summarize(qrels, runs, restrict_to=None):
    """Nhiều seed → trung bình ± SD; điểm từng truy vấn = trung bình qua seed."""
    if not runs:
        return None
    ms = [evaluate(qrels, r, restrict_to=restrict_to) for r in runs]
    keys = ms[0].keys()
    out = {k: float(np.mean([m[k] for m in ms])) for k in keys}
    out.update({f"{k}_sd": float(np.std([m[k] for m in ms])) for k in keys} if len(ms) > 1 else {})
    pq = [per_query(qrels if restrict_to is None else {q: v for q, v in qrels.items() if q in set(restrict_to)}, r)
          for r in runs]
    out["per_query"] = {q: float(np.mean([p[q] for p in pq])) for q in pq[0]}
    out["n_runs"] = len(runs)
    return out


# ---------------------------------------------------------------- E0
def e0():
    rows = []
    for s in SYSTEMS:
        if not s.anchor:
            continue
        pub = PUB.row(s.anchor)[3]
        tol = PUB.E0_TOL["bm25"] if s.sid == "R0" else PUB.E0_TOL["default"]
        for ds in BEIR3:
            runs = load_runs(s, ds)
            if not runs:
                rows.append({"system": s.sid, "label": s.label, "ds": ds, "ours": None, "paper": pub[ds]})
                continue
            ours = 100 * evaluate(qrels_for(ds), runs[0])["nDCG@10"]
            row = {"system": s.sid, "label": s.label, "ds": ds, "ours": round(ours, 2), "paper": pub[ds],
                   "diff": round(ours - pub[ds], 2), "tol": tol, "pass": abs(ours - pub[ds]) <= tol,
                   "pyserini_2cr": PUB.PYSERINI_BM25_FLAT.get(ds) if s.sid == "R0" else None}
            rk = load_runs(s, ds, suffix=".rk")      # cấu hình giống Rankify: chỉ abstract, fp32
            if rk:
                o = 100 * evaluate(qrels_for(ds), rk[0])["nDCG@10"]
                row.update({"ours_rk": round(o, 2), "diff_rk": round(o - pub[ds], 2), "pass_rk": abs(o - pub[ds]) <= tol})
            rows.append(row)
    write_json(RESULTS / "e0" / "e0.json", rows)
    return rows


# ---------------------------------------------------------------- E1
def e1():
    res = {}
    for ds in BEIR3:
        q = qrels_for(ds)
        table = {}
        for s in SYSTEMS:
            m = summarize(q, load_runs(s, ds))
            table[s.sid] = m
        for base in ("R0", "R4"):
            if not table.get(base):
                continue
            ids = [sid for sid in table if table[sid] and sid != base]
            tests = [paired_bootstrap(table[sid]["per_query"], table[base]["per_query"]) for sid in ids]
            adj = holm([t["p"] for t in tests])
            for sid, t, pa in zip(ids, tests, adj):
                table[sid][f"vs_{base}"] = {**t, "p_holm": pa, "sig": pa < 0.05}
        for sid, m in table.items():
            if m:
                m["ci95"] = mean_ci(m["per_query"])
        res[ds] = table
    write_json(RESULTS / "e1" / "e1.json", strip_pq(res))
    write_json(RESULTS / "e1" / "e1_per_query.json", {ds: {s: (m or {}).get("per_query") for s, m in t.items()} for ds, t in res.items()})
    return res


def strip_pq(obj):
    if isinstance(obj, dict):
        return {k: strip_pq(v) for k, v in obj.items() if k != "per_query"}
    return obj


# ---------------------------------------------------------------- E2
VARIANTS = [("Q-q", False), ("Q-kw", False), ("Q-qn", False), ("Q-q", True), ("Q-kw", True), ("Q-qn", True)]


def suffix(variant, meta):
    return ("" if variant == "Q-q" else f".{variant}") + (".M1" if meta else "")


def e2():
    ds, q = "trec-covid", qrels_for("trec-covid")
    out = {"variants": {}, "bm25_first_stage": {}, "criteria": {}, "listwise_vs_pointwise": {}, "position_bias": {},
           "lambdamart_cv": {}, "mesh_boost": {}}
    for sid in ("R2", "R2b", "R3", "R4", "R5s", "R6"):
        s = BY_ID[sid]
        row = {}
        for v, m in VARIANTS:
            r = summarize(q, load_runs(s, ds, suffix=suffix(v, m)))
            row[f"{v}{'+M1' if m else ''}"] = None if r is None else {"nDCG@10": r["nDCG@10"], "sd": r.get("nDCG@10_sd")}
        out["variants"][sid] = row
    for v in ("Q-q", "Q-kw", "Q-qn"):
        p = RUNS / ds / "test" / f"bm25{'' if v == 'Q-q' else '.' + v}.trec"
        out["bm25_first_stage"][v] = evaluate(q, read_run(p))["nDCG@10"] if p.exists() else None
    for name, crit in (("R6", "jev.crit"), ("R5s", "gpt_small.crit")):
        for d in BEIR3:
            qq = qrels_for(d)
            base = summarize(qq, load_runs(BY_ID[name], d))
            c = [read_run(RUNS / d / "test" / f"{crit}.trec")] if (RUNS / d / "test" / f"{crit}.trec").exists() else []
            cm = summarize(qq, c)
            out["criteria"].setdefault(name, {})[d] = {
                "generic": base and base["nDCG@10"], "domain": cm and cm["nDCG@10"],
                "test": paired_bootstrap(cm["per_query"], base["per_query"]) if base and cm else None}
    for d in BEIR3:
        qq = qrels_for(d)
        lw = summarize(qq, load_runs(BY_ID["R6"], d))
        pw_p = RUNS / d / "test" / "jev_pw.trec"
        pw = summarize(qq, [read_run(pw_p)]) if pw_p.exists() else None
        out["listwise_vs_pointwise"][d] = {"listwise": lw and lw["nDCG@10"], "pointwise": pw and pw["nDCG@10"]}
    for name in ("gpt_small", "jev"):
        for d in ("trec-covid", "nfcorpus"):
            paths = [RUNS / d / "test" / f"{name}.shuf{k}.trec" for k in (1, 2, 3)]
            base = RUNS / d / "test" / f"{name}.trec"
            if not all(p.exists() for p in paths) or not base.exists():
                out["position_bias"].setdefault(name, {})[d] = None
                continue
            runs = [read_run(base)] + [read_run(p) for p in paths]
            out["position_bias"].setdefault(name, {})[d] = position_bias(runs, qrels_for(d))
    for meta in (False, True):
        r = summarize(q, [read_run(p) for p in sorted((RUNS / ds / "test").glob(f"lambdamart_cv_s?{'.M1' if meta else ''}.trec"))])
        out["lambdamart_cv"]["M1" if meta else "M0"] = r and {"nDCG@10": r["nDCG@10"], "sd": r.get("nDCG@10_sd")}
    out["mesh_boost"] = mesh_boost(q)
    write_json(RESULTS / "e2" / "e2.json", out)
    return out


def position_bias(runs, qrels):
    from scipy.stats import kendalltau
    taus = []
    common = set.intersection(*[set(r) for r in runs])
    for qid in common:
        orders = [sorted(r[qid], key=lambda d: -r[qid][d]) for r in runs]
        ref = {d: i for i, d in enumerate(orders[0])}
        for o in orders[1:]:
            t, _ = kendalltau([ref[d] for d in o if d in ref], list(range(len([d for d in o if d in ref]))))
            taus.append(t)
    nd = [evaluate(qrels, r, restrict_to=common)["nDCG@10"] for r in runs]
    return {"mean_tau_vs_original": float(np.nanmean(taus)), "ndcg10_original": nd[0],
            "ndcg10_shuffled": nd[1:], "ndcg10_range": float(max(nd) - min(nd)), "n_queries": len(common)}


def mesh_boost(q, grid=(0.0, 0.1, 0.25, 0.5, 1.0, 2.0), n_folds=5):
    """score' = z(score) + λ·overlap_MeSH, λ chọn bằng CV 5-fold theo topic (không chỉnh trên topic đang chấm)."""
    dm, tm = metadata.doc_meta(), metadata.topic_mesh()
    if not dm or not tm:
        return {}
    topics = sorted(q, key=int)
    fold = {t: i % n_folds for i, t in enumerate(topics)}

    def overlap(qid, did):
        qm = set(tm.get(qid, {}).get("mesh", []))
        mesh = {x["descriptor"].lower() for x in (dm.get(did) or {}).get("mesh", [])}
        return len(qm & mesh) / max(len(qm), 1)

    out = {}
    for s in SYSTEMS:
        runs = load_runs(s, "trec-covid")
        if not runs:
            continue
        r = runs[0]
        z = {}
        for qid, docs in r.items():
            v = np.array(list(docs.values()))
            mu, sd = v.mean(), v.std() + 1e-9
            z[qid] = {d: (sc - mu) / sd for d, sc in docs.items()}

        def boosted(lam, qids):
            return {qid: {d: sc + lam * overlap(qid, d) for d, sc in z[qid].items()} for qid in qids if qid in z}

        held = {}
        lams = []
        for f in range(n_folds):
            tr = [t for t in topics if fold[t] != f]
            te = [t for t in topics if fold[t] == f]
            best = max(grid, key=lambda lam: evaluate(q, boosted(lam, tr), restrict_to=tr)["nDCG@10"])
            lams.append(best)
            held.update(boosted(best, te))
        base = evaluate(q, r)["nDCG@10"]
        new = evaluate(q, held)["nDCG@10"]
        out[s.sid] = {"base": base, "boosted_cv": new, "delta": new - base, "lambdas": lams,
                      "test": paired_bootstrap(per_query(q, held), per_query(q, r))}
    return out


# ---------------------------------------------------------------- E3
def condense(run, qrels):
    return {q: {d: s for d, s in docs.items() if d in qrels.get(q, {})} for q, docs in run.items()}


def e3():
    out = {"scifact_open": {}, "trec_covid_rounds": {}}
    qo, qn = scifact_open.qrels("orig"), scifact_open.qrels("open")
    both = sorted(set(qo) & set(qn))
    for scope, restrict in (("intersection", both), ("all", None)):
        sc_o, sc_n, rows = {}, {}, {}
        for s in SYSTEMS:
            runs = load_runs(s, "scifact-open")
            if not runs:
                continue
            mo, mn = summarize(qo, runs, restrict), summarize(qn, runs, restrict)
            sc_o[s.sid], sc_n[s.sid] = mo["nDCG@10"], mn["nDCG@10"]
            rows[s.sid] = {"orig": mo["nDCG@10"], "open": mn["nDCG@10"], "delta": mn["nDCG@10"] - mo["nDCG@10"],
                           "judged10_orig": mo["Judged@10"], "judged10_open": mn["Judged@10"],
                           "R@10_orig": mo["R@10"], "R@10_open": mn["R@10"]}
        out["scifact_open"][scope] = {"systems": rows, "kendall": kendall(sc_o, sc_n) if len(sc_o) > 1 else None,
                                      "n_claims": len(both) if restrict else None}
    # TREC-COVID: nhãn tích lũy tới hết vòng r (r = 1..4) so với nhãn đầy đủ, trên 30 topic có từ vòng 1.
    # Thêm nDCG@10 "condensed" (bỏ bài chưa có nhãn khỏi danh sách trước khi chấm — Sakai 2007).
    full = trec_covid.full_qrels_round1_topics()
    topics = sorted(full, key=int)
    all_runs = {s.sid: load_runs(s, "trec-covid") for s in SYSTEMS}
    all_runs = {k: v for k, v in all_runs.items() if v}
    sc_f = {sid: summarize(full, runs, topics)["nDCG@10"] for sid, runs in all_runs.items()}
    levels = {}
    for lvl in (1.0, 2.0, 3.0, 4.0):
        ql = trec_covid.round_qrels(lvl)
        rows, sc_l, sc_c = {}, {}, {}
        for sid, runs in all_runs.items():
            ml = summarize(ql, runs, topics)
            mc = summarize(ql, [condense(r, ql) for r in runs], topics)
            sc_l[sid], sc_c[sid] = ml["nDCG@10"], mc["nDCG@10"]
            rows[sid] = {"shallow": ml["nDCG@10"], "condensed": mc["nDCG@10"], "full": sc_f[sid],
                         "judged10_shallow": ml["Judged@10"]}
        levels[str(lvl)] = {"systems": rows, "n_pairs": sum(len(v) for v in ql.values()),
                            "kendall": kendall(sc_l, sc_f) if len(sc_l) > 1 else None,
                            "kendall_condensed": kendall(sc_c, sc_f) if len(sc_c) > 1 else None}
    out["trec_covid_rounds"] = {"levels": levels, "n_topics": len(topics), "report": trec_covid.rounds_report()}
    write_json(RESULTS / "e3" / "e3.json", out)
    return out


# ---------------------------------------------------------------- E4
def e4():
    pricing = load_yaml("pricing.yaml")
    t4 = pricing["gpu"]["t4_usd_per_hour"]
    rows = {}
    lat = defaultdict(list)
    name_map = {"medcpt_ce": "R3", "bge_v2_m3": "R4", "bge_base": "X1", "bge_large": "X2", "mxbai_base": "X3",
                "monot5_base": "X4", "qwen3_4b": "R7"}
    task_sid = {"crossenc": None, "bilstm": "R2", "bilstm2": "R2b", "qwen3": None}   # None: lấy theo trường model
    gpus = {}
    for task, fixed in task_sid.items():
        p = RESULTS / "kaggle" / task / "out" / "latency.jsonl"
        if p.exists():
            for r in read_jsonl(p):
                if r["ds"] in BEIR3 and "." not in r["variant"] and r["n_docs"] >= 90:
                    sid = fixed or name_map.get(r["model"], r["model"])
                    lat[sid].append(r["ms"])
                    gpus[sid] = r.get("parallel_gpus", 1)
    for sid, v in lat.items():
        v = np.array(v)
        rows[sid] = {"kind": "local-gpu", "device": f"Tesla T4 (Kaggle) ×{gpus.get(sid, 1)} song song", "n": len(v),
                     "p50_ms": float(np.percentile(v, 50)), "p95_ms": float(np.percentile(v, 95)),
                     "p99_ms": float(np.percentile(v, 99)),
                     "usd_per_1k": float(v.mean() / 1000 / 3600 * t4 * 1000), "usd_note": f"ước lượng: giá thuê T4 {t4} USD/giờ"}
    for name, sid in (("gpt_small", "R5s"), ("gpt_large", "R5l"), ("jev", "R6")):
        logs = [p for p in (RESULTS / "api_logs").glob(f"{name}__*.jsonl") if p.name.split("__")[1].replace(".jsonl", "") in BEIR3]
        recs = [r for p in logs for r in read_jsonl(p) if not r["cache_hit"]]
        if not recs:
            continue
        per_q = defaultdict(lambda: {"ms": 0.0, "usd": 0.0, "req": 0})
        for r in recs:
            k = (r["run_id"], r["query_id"])
            per_q[k]["ms"] += r["latency_ms"]
            per_q[k]["usd"] += r["cost_usd"]
            per_q[k]["req"] += r["n_requests"]
        ms = np.array([v["ms"] for v in per_q.values()])
        rows[sid] = {"kind": "api", "n": len(per_q), "p50_ms": float(np.percentile(ms, 50)),
                     "p95_ms": float(np.percentile(ms, 95)), "p99_ms": float(np.percentile(ms, 99)),
                     "usd_per_1k": float(np.mean([v["usd"] for v in per_q.values()]) * 1000),
                     "requests_per_query": float(np.mean([v["req"] for v in per_q.values()])),
                     "errors": sum(r["status"] != "ok" for r in recs),
                     "usd_note": "giá trong configs/pricing.yaml; latency tuần tự (không tính song song)"}
    e1r = json.loads((RESULTS / "e1" / "e1.json").read_text()) if (RESULTS / "e1" / "e1.json").exists() else {}
    for sid, r in rows.items():
        vals = [e1r.get(ds, {}).get(sid, {}) for ds in BEIR3]
        nd = [v["nDCG@10"] for v in vals if v]
        r["mean_ndcg10_beir3"] = float(np.mean(nd)) if len(nd) == 3 else None
    rows["R0"] = rows.get("R0") or {"kind": "local-cpu", "p50_ms": None, "usd_per_1k": 0.0,
                                    "mean_ndcg10_beir3": float(np.mean([e1r[d]["R0"]["nDCG@10"] for d in BEIR3])) if e1r else None}
    write_json(RESULTS / "e4" / "e4.json", rows)
    return rows


STEPS = {"e0": e0, "e1": e1, "e2": e2, "e3": e3, "e4": e4}

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="*", choices=list(STEPS))
    a = ap.parse_args()
    for k in a.only or list(STEPS):
        STEPS[k]()
        print(f"✓ {k} → results/{k}/", flush=True)
