"""Suy vector cho từ không có trong BioWordVec (OOV) từ ngữ cảnh trong kho tài liệu (không dùng nhãn).

Với mỗi từ OOV xuất hiện trong corpus/truy vấn của gói dữ liệu: vector = trung bình vector BioWordVec của các từ
lân cận (cửa sổ ±5) qua tối đa 300 lần xuất hiện, có trọng số SIF a/(a+p(w)) và bỏ stopword, rồi trừ thành phần
chung của mọi vector suy ra (Arora et al., 2017) — bản đơn giản của "à la carte embedding" (Khodak et al., 2018).
Ví dụ "covid-19" lấy ngữ cảnh "coronavirus disease 2019 pandemic…".
Ra: data/kaggle_pack/emb_v2/{emb.npy (float16), found.npy, imputed.npy, words.json, stats.json}
"""
import json
import re
from collections import Counter, defaultdict

import numpy as np

from ..utils.io import read_jsonl
from ..utils.paths import PACK, RESULTS

TOKEN = re.compile(r"[a-z0-9]+(?:[-'][a-z0-9]+)*")
WINDOW, MAX_OCC, MIN_CTX, SIF_A = 5, 300, 3, 1e-3
STOP = set("""a about above after again against all am an and any are as at be because been before being below between
both but by can could did do does doing down during each few for from further had has have having he her here hers
him his how i if in into is it its itself just me more most my no nor not now of off on once only or other our out
over own same she should so some such than that the their them then there these they this those through to too under
until up very was we were what when where which while who whom why will with would you your also however thus may
might must one two three using used use within without among via et al""".split())
SRC = RESULTS / "kaggle" / "biowordvec_cut" / "out"


def texts():
    for p in sorted((PACK / "corpus").glob("*.jsonl")):
        for d in read_jsonl(p):
            yield f'{d.get("title", "")} {d.get("text", "")}'
    for p in sorted((PACK / "queries").glob("*.jsonl")):
        for q in read_jsonl(p):
            yield q["text"]


def context_vectors(docs, targets, weight, emb, max_occ):
    """Trung bình có trọng số SIF của vector các từ lân cận (±WINDOW) quanh mỗi từ đích."""
    acc = {t: np.zeros(emb.shape[1]) for t in targets}
    wsum = defaultdict(float)
    nctx, occ = defaultdict(int), defaultdict(int)
    for ids in docs:
        for i, wi in enumerate(ids):
            if wi not in acc or occ[wi] >= max_occ:
                continue
            occ[wi] += 1
            for j in range(max(0, i - WINDOW), min(len(ids), i + WINDOW + 1)):
                w_c = weight.get(ids[j]) if j != i else None
                if w_c:
                    acc[wi] += w_c * emb[ids[j]]
                    wsum[wi] += w_c
                    nctx[wi] += 1
    return {t: acc[t] / wsum[t] for t in targets if nctx[t] >= MIN_CTX}


def build(n_train=6000, ridge=1.0, seed=0):
    """À la carte (Khodak et al., 2018): học A sao cho A·(ngữ cảnh TB của w) ≈ vector BioWordVec của w trên các từ
    đã có vector, rồi áp A cho từ OOV. Đánh giá A trên 10% từ giữ lại (cosine với vector thật)."""
    words = json.loads((SRC / "words.json").read_text())
    emb = np.load(SRC / "emb.npy").astype(np.float32)
    found = np.load(SRC / "found.npy")
    idx = {w: i for i, w in enumerate(words)}
    docs = [[idx.get(w, -1) for w in TOKEN.findall(t.lower())] for t in texts()]
    freq = Counter(i for d in docs for i in d if i >= 0)
    total = sum(freq.values())
    stop_ids = {idx[w] for w in STOP if w in idx}
    weight = {i: SIF_A / (SIF_A + n / total) for i, n in freq.items() if i not in stop_ids and found[i]}
    rng = np.random.default_rng(seed)
    cand = [i for i, n in freq.items() if found[i] and i not in stop_ids and n >= 20]
    train_words = list(rng.choice(cand, size=min(n_train, len(cand)), replace=False))
    oov_words = [i for i in freq if not found[i]]
    ctx = context_vectors(docs, set(train_words) | set(oov_words), weight, emb, MAX_OCC)
    tw = [i for i in train_words if i in ctx]
    rng.shuffle(tw)
    n_val = len(tw) // 10
    val, fit = tw[:n_val], tw[n_val:]
    X, Y = np.stack([ctx[i] for i in fit]), emb[fit]
    A = np.linalg.solve(X.T @ X + ridge * np.eye(X.shape[1]), X.T @ Y)

    def cos(a, b):
        return float(np.mean(np.sum(a * b, 1) / (np.linalg.norm(a, axis=1) * np.linalg.norm(b, axis=1) + 1e-9)))
    Xv = np.stack([ctx[i] for i in val])
    val_cos = cos(Xv @ A, emb[val])
    val_cos_raw = cos(Xv, emb[val])           # không biến đổi (trung bình ngữ cảnh thuần) để so
    imputed = np.zeros(len(words), bool)
    for i in oov_words:
        if i in ctx:
            emb[i] = (ctx[i] @ A).astype(np.float32)
            imputed[i] = True
    out = PACK / "emb_v2"
    out.mkdir(parents=True, exist_ok=True)
    np.save(out / "emb.npy", emb.astype(np.float16))
    np.save(out / "found.npy", found)
    np.save(out / "imputed.npy", imputed)
    (out / "words.json").write_text(json.dumps(words))
    norm = emb / (np.linalg.norm(emb, axis=1, keepdims=True) + 1e-9)
    content = found & np.array([w not in STOP for w in words])
    fw = np.array(words)[content]
    probe = {}
    for w in ("covid-19", "sars-cov-2", "covid", "2019-ncov", "mrna-1273"):
        if w in idx and imputed[idx[w]]:
            sims = norm[content] @ norm[idx[w]]
            probe[w] = [str(fw[k]) for k in np.argsort(-sims)[:8]]
    stats = {"vocab": len(words), "found": int(found.sum()), "oov": int((~found).sum()), "imputed": int(imputed.sum()),
             "coverage_after": round(float((found | imputed).mean()), 4),
             "alacarte_fit_words": len(fit), "alacarte_val_words": len(val),
             "val_cosine_alacarte": round(val_cos, 4), "val_cosine_context_mean": round(val_cos_raw, 4),
             "nearest_neighbours": probe, "window": WINDOW, "max_occurrences": MAX_OCC, "min_context_words": MIN_CTX}
    (out / "stats.json").write_text(json.dumps(stats, indent=1, ensure_ascii=False))
    return stats


if __name__ == "__main__":
    print(json.dumps(build(), indent=1, ensure_ascii=False))
