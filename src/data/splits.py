"""Chia train/dev/test và kiểm tra rò rỉ (mục 4.4 của plan).

- test: split test của BEIR (3 bộ) + 279 claim SciFact-Open. Không bao giờ dùng để chỉnh tham số.
- dev:  324 câu dev NFCorpus + 20% claim train SciFact (seed 0).
- train: train NFCorpus + 80% còn lại của train SciFact. TREC-COVID không có train.
- Câu train gần trùng (TF-IDF cosine > 0,9) với bất kỳ câu test nào bị loại khỏi train.
"""
import random

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from ..utils.io import read_json, read_jsonl, write_json
from ..utils.paths import PROC, RAW, RESULTS
from . import scifact_open
from .beir_loader import load_qrels, load_queries

SPLITS_FILE = PROC / "splits.json"
DEV_FRAC, SEED, DUP_THRESHOLD = 0.2, 0, 0.9


def build():
    nf_train = sorted(load_qrels("nfcorpus", "train"))
    nf_dev = sorted(load_qrels("nfcorpus", "dev"))
    sf_train_all = sorted(load_qrels("scifact", "train"), key=int)
    rng = random.Random(SEED)
    sf_dev = sorted(rng.sample(sf_train_all, round(DEV_FRAC * len(sf_train_all))), key=int)
    sf_train = [q for q in sf_train_all if q not in set(sf_dev)]

    tests = {
        "trec-covid": sorted(load_qrels("trec-covid", "test"), key=int),
        "nfcorpus": sorted(load_qrels("nfcorpus", "test")),
        "scifact": sorted(load_qrels("scifact", "test"), key=int),
        "scifact-open": sorted(scifact_open.claims(), key=int),
    }

    # --- rò rỉ theo ID claim của SciFact
    orig = RAW / "scifact_orig" / "data"
    id_report = {}
    if orig.exists():
        dev_ids = {str(r["id"]) for r in read_jsonl(orig / "claims_dev.jsonl")}
        test_ids = {str(r["id"]) for r in read_jsonl(orig / "claims_test.jsonl")}
        id_report = {
            "beir_scifact_test_is_orig_dev": set(tests["scifact"]) <= dev_ids and len(tests["scifact"]) == len(dev_ids),
            "scifact_open_subset_of_orig_test": set(tests["scifact-open"]) <= test_ids,
            "train_overlap_beir_test": len(set(sf_train_all) & set(tests["scifact"])),
            "train_overlap_scifact_open": len(set(sf_train_all) & set(tests["scifact-open"])),
        }

    # --- câu gần trùng giữa train và mọi test
    qtext = {}
    for ds in ("nfcorpus", "scifact", "trec-covid"):
        qtext.update({(ds, q): t for q, t in load_queries(ds).items()})
    qtext.update({("scifact-open", q): t for q, t in scifact_open.queries().items()})
    train_keys = [("nfcorpus", q) for q in nf_train] + [("scifact", q) for q in sf_train]
    test_keys = [(ds, q) for ds, qs in tests.items() for q in qs]
    vec = TfidfVectorizer(lowercase=True, ngram_range=(1, 2), min_df=1, token_pattern=r"(?u)\b\w+\b").fit(
        [qtext[k] for k in train_keys + test_keys])
    sim = cosine_similarity(vec.transform([qtext[k] for k in train_keys]), vec.transform([qtext[k] for k in test_keys]))
    drop = {}
    for i, k in enumerate(train_keys):
        j = sim[i].argmax()
        if sim[i, j] > DUP_THRESHOLD:
            drop[k] = (test_keys[j], float(sim[i, j]))
    nf_train_f = [q for q in nf_train if ("nfcorpus", q) not in drop]
    sf_train_f = [q for q in sf_train if ("scifact", q) not in drop]

    splits = {
        "trec-covid": {"test": tests["trec-covid"]},
        "nfcorpus": {"train": nf_train_f, "dev": nf_dev, "test": tests["nfcorpus"]},
        "scifact": {"train": sf_train_f, "dev": sf_dev, "test": tests["scifact"]},
        "scifact-open": {"test": tests["scifact-open"]},
    }
    write_json(SPLITS_FILE, splits)
    report = {
        "sizes": {ds: {s: len(v) for s, v in d.items()} for ds, d in splits.items()},
        "claim_id_checks": id_report,
        "near_duplicate_threshold": DUP_THRESHOLD,
        "dropped_from_train": len(drop),
        "dropped_by_dataset": {ds: sum(k[0] == ds for k in drop) for ds in ("nfcorpus", "scifact")},
        "dropped_examples": [
            {"train": f"{k[0]}:{k[1]}", "train_text": qtext[k], "test": f"{t[0]}:{t[1]}", "test_text": qtext[t], "cos": round(s, 3)}
            for k, (t, s) in list(drop.items())[:15]],
    }
    write_json(RESULTS / "data_report" / "splits.json", report)
    return splits, report


def load() -> dict:
    if not SPLITS_FILE.exists():
        build()
    return read_json(SPLITS_FILE)


if __name__ == "__main__":
    import json
    _, rep = build()
    print(json.dumps({k: v for k, v in rep.items() if k != "dropped_examples"}, ensure_ascii=False, indent=1))
