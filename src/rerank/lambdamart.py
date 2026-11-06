"""R1 — LambdaMART (LightGBM lambdarank) trên BM25 top-100.

Hai chế độ:
- main: train NFCorpus + SciFact (train), early stopping trên dev → dự đoán 4 bộ test (TREC-COVID zero-shot).
- cv:   TREC-COVID 5-fold theo topic (E2), so M0 với M1 (đặc trưng metadata) — vì train NFCorpus/SciFact
        không có metadata nên không học được trọng số metadata ở chế độ main.
Chạy: python -m src.rerank.lambdamart [--mode main|cv|all]
"""
import argparse
import math
import re

import lightgbm as lgb
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

from ..data import metadata
from ..data.beir_loader import load_qrels
from ..kaggle_tasks.common import doc_text
from ..utils.io import write_json, write_run
from ..utils.paths import RESULTS, RUNS
from .candidates import pack

TOKEN = re.compile(r"[a-z0-9]+(?:[-'][a-z0-9]+)*")
STOP = set("a an and are as at be by for from has have how in is it of on or that the this to was were what when "
           "which who why will with does do can".split())
FEATS_M0 = ["bm25", "bm25_rank", "bm25_norm", "tfidf", "medcpt", "medcpt_z", "q_overlap", "title_overlap",
            "doc_len", "q_len", "has_title"]
FEATS_M1 = FEATS_M0 + ["year", "is_2020", "has_mesh", "n_mesh", "mesh_overlap", "pt_review", "pt_trial", "pt_case",
                       "has_pmid"]
SEEDS = (0, 1, 2)
MEDCPT_DIR = RESULTS / "kaggle" / "medcpt_feat" / "out" / "feats" / "medcpt"


def toks(s):
    return [t for t in TOKEN.findall(s.lower()) if t not in STOP]


_TFIDF = {}


def tfidf_for(ds):
    if ds not in _TFIDF:
        corpus = pack().corpus(ds)
        ids = list(corpus)
        vec = TfidfVectorizer(sublinear_tf=True, token_pattern=r"(?u)\b\w+\b", min_df=1)
        M = vec.fit_transform([doc_text(corpus[d]) for d in ids])
        _TFIDF[ds] = (vec, M, {d: i for i, d in enumerate(ids)})
    return _TFIDF[ds]


def medcpt_scores(ds, split):
    p = MEDCPT_DIR / f"{ds}__{split}.tsv"
    out = {}
    if p.exists():
        for line in open(p):
            q, d, s = line.rstrip("\n").split("\t")
            out[(q, d)] = float(s)
    return out


def features(ds, split, meta=False):
    """→ keys [(qid, docid)], X (n×f), feature names."""
    P = pack()
    corpus, cand, queries = P.corpus(ds), P.run(ds, split), P.queries(ds, split, "Q-q")
    vec, M, pos = tfidf_for(ds)
    med = medcpt_scores(ds, split)
    dmeta = metadata.doc_meta() if (meta and ds == "trec-covid") else {}
    tmesh = metadata.topic_mesh() if (meta and ds == "trec-covid") else {}
    names = FEATS_M1 if meta else FEATS_M0
    keys, rows = [], []
    for qid, qtext in queries.items():
        lst = cand.get(qid, [])
        if not lst:
            continue
        qv = vec.transform([qtext])
        dids = [d for d, _ in lst]
        tf = (M[[pos[d] for d in dids]] @ qv.T).toarray().ravel()
        qt = set(toks(qtext))
        bm = np.array([s for _, s in lst])
        mc = np.array([med.get((qid, d), np.nan) for d in dids])
        mz = (mc - np.nanmean(mc)) / (np.nanstd(mc) + 1e-6) if np.isfinite(mc).any() else mc
        qmesh = set(tmesh.get(qid, {}).get("mesh", []))
        for r, d in enumerate(dids):
            doc = corpus[d]
            dt = set(toks(doc_text(doc)))
            tt = set(toks(doc.get("title") or ""))
            f = {
                "bm25": bm[r], "bm25_rank": r + 1, "bm25_norm": bm[r] / (bm[0] + 1e-9), "tfidf": tf[r],
                "medcpt": mc[r], "medcpt_z": mz[r],
                "q_overlap": len(qt & dt) / max(len(qt), 1), "title_overlap": len(qt & tt) / max(len(qt), 1),
                "doc_len": math.log1p(len(dt)), "q_len": len(qt), "has_title": float(bool(doc.get("title"))),
            }
            if meta:
                m = dmeta.get(d) or {}
                mesh = {x["descriptor"].lower() for x in m.get("mesh", [])}
                pts = " ".join(m.get("pub_types", [])).lower()
                f.update({
                    "year": m.get("year") or np.nan, "is_2020": float(m.get("year") == 2020),
                    "has_mesh": float(bool(mesh)), "n_mesh": len(mesh),
                    "mesh_overlap": len(qmesh & mesh) / max(len(qmesh), 1) if mesh else np.nan,
                    "pt_review": float("review" in pts), "pt_trial": float("trial" in pts),
                    "pt_case": float("case report" in pts), "has_pmid": float(bool(m.get("pubmed_id"))),
                })
            keys.append((qid, d))
            rows.append([f[n] for n in names])
    return keys, np.array(rows, dtype=np.float64), names


def labels(keys, qrels):
    return np.array([max(0, qrels.get(q, {}).get(d, 0)) for q, d in keys])


def groups(keys):
    g, last, n = [], None, 0
    for q, _ in keys:
        if q != last and last is not None:
            g.append(n)
            n = 0
        last = q
        n += 1
    if n:
        g.append(n)
    return g


def to_run(keys, scores):
    run = {}
    for (q, d), s in zip(keys, scores):
        run.setdefault(q, {})[d] = float(s)
    return run


def model(seed):
    return lgb.LGBMRanker(objective="lambdarank", n_estimators=1000, learning_rate=0.05, num_leaves=31,
                          min_child_samples=50, subsample=0.8, subsample_freq=1, colsample_bytree=0.8,
                          random_state=seed, verbose=-1)


def _stack(parts):
    keys = [k for p in parts for k in p[0]]
    X = np.vstack([p[1] for p in parts])
    return keys, X


def train_main():
    P = pack()
    tr = [features("nfcorpus", "train"), features("scifact", "train")]
    dv = [features("nfcorpus", "dev"), features("scifact", "dev")]
    # qrels: ID truy vấn của NFCorpus ("PLAIN-…") và SciFact (số) không trùng nhau, gộp an toàn
    q_tr = {**P.qrels("nfcorpus", "train"), **P.qrels("scifact", "train")}
    q_dv = {**P.qrels("nfcorpus", "dev"), **P.qrels("scifact", "dev")}
    ktr, Xtr = _stack(tr)
    kdv, Xdv = _stack(dv)
    ytr, ydv = labels(ktr, q_tr), labels(kdv, q_dv)
    names = tr[0][2]
    report = {"features": names, "seeds": {}}
    tests = {ds: features(ds, "test") for ds in ("trec-covid", "nfcorpus", "scifact", "scifact-open")}
    for seed in SEEDS:
        m = model(seed)
        m.fit(Xtr, ytr, group=groups(ktr), eval_set=[(Xdv, ydv)], eval_group=[groups(kdv)], eval_at=[10],
              callbacks=[lgb.early_stopping(50, verbose=False)])
        report["seeds"][seed] = {"best_iteration": int(m.best_iteration_ or 0),
                                 "dev_ndcg10": float(m.best_score_["valid_0"]["ndcg@10"]),
                                 "importance_gain": dict(zip(names, m.booster_.feature_importance("gain").round(2).tolist()))}
        for ds, (k, X, _) in tests.items():
            write_run(RUNS / ds / "test" / f"lambdamart_s{seed}.trec", to_run(k, m.predict(X)), f"lambdamart_s{seed}")
        print(f"LambdaMART seed {seed}: dev nDCG@10 {report['seeds'][seed]['dev_ndcg10']:.4f}, iter {m.best_iteration_}", flush=True)
    write_json(RESULTS / "e1" / "lambdamart_train.json", report)
    return report


def train_cv(n_folds=5):
    """TREC-COVID: 5-fold theo topic, fold cuối của phần train làm validation để early stopping."""
    qrels = load_qrels("trec-covid", "test")
    report = {}
    for meta in (False, True):
        keys, X, names = features("trec-covid", "test", meta=meta)
        y = labels(keys, qrels)
        topics = sorted({q for q, _ in keys}, key=int)
        fold = {q: i % n_folds for i, q in enumerate(topics)}
        imp = np.zeros(len(names))
        for seed in SEEDS:
            scores = np.zeros(len(keys))
            for f in range(n_folds):
                val_f = (f + 1) % n_folds
                te = np.array([fold[q] == f for q, _ in keys])
                va = np.array([fold[q] == val_f for q, _ in keys])
                tr = ~te & ~va
                ktr = [k for k, b in zip(keys, tr) if b]
                kva = [k for k, b in zip(keys, va) if b]
                m = model(seed)
                m.fit(X[tr], y[tr], group=groups(ktr), eval_set=[(X[va], y[va])], eval_group=[groups(kva)],
                      eval_at=[10], callbacks=[lgb.early_stopping(50, verbose=False)])
                scores[te] = m.predict(X[te])
                imp += m.booster_.feature_importance("gain")
            name = f"lambdamart_cv_s{seed}" + (".M1" if meta else "")
            write_run(RUNS / "trec-covid" / "test" / f"{name}.trec", to_run(keys, scores), name)
        report["M1" if meta else "M0"] = {"features": names,
                                          "importance_gain": dict(zip(names, (imp / imp.sum()).round(4).tolist()))}
        print(f"LambdaMART CV {'M1' if meta else 'M0'} xong", flush=True)
    write_json(RESULTS / "e2" / "lambdamart_cv.json", report)
    return report


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", default="all", choices=["main", "cv", "all"])
    a = ap.parse_args()
    if a.mode in ("main", "all"):
        train_main()
    if a.mode in ("cv", "all"):
        train_cv()
