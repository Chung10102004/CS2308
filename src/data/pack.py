"""Đóng gói dữ liệu cho Kaggle: corpus (chỉ bài xuất hiện trong ứng viên), truy vấn, run BM25 top-100,
qrels train/dev (cho R2), vocab cho BioWordVec, cùng mã nguồn `src/`. KHÔNG kèm qrels test.

Bố cục data/kaggle_pack/:
  PACK_MANIFEST.json
  corpus/<bộ>.jsonl            {"docid","title","text","meta"}  (meta = dòng M1, chỉ TREC-COVID)
  queries/<bộ>__<split>__<biến thể>.jsonl   {"qid","text"}
  runs/<bộ>__<split>.trec      BM25 top-100 (biến thể Q-q; ứng viên cố định cho mọi reranker)
  qrels/<bộ>__{train,dev}.tsv
  vocab.txt
  code/src/…, code/requirements-kaggle.txt
"""
import json
import re
import shutil
from collections import Counter

from ..utils.io import read_run, write_jsonl
from ..utils.paths import PACK, ROOT, RUNS
from . import metadata, scifact_open, splits, trec_covid
from .beir_loader import load_corpus, load_qrels, load_queries

TOKEN = re.compile(r"[a-z0-9]+(?:[-'][a-z0-9]+)*")
VOCAB_MAX = 300_000


def tokenize(text: str) -> list:
    return TOKEN.findall(text.lower())


def _queries_for(ds):
    sp = splits.load()[ds]
    out = []
    if ds == "scifact-open":
        q = scifact_open.queries()
        out.append(("test", "Q-q", {i: q[i] for i in sp["test"]}))
        return out
    q = load_queries(ds)
    for split, qids in sp.items():
        out.append((split, "Q-q", {i: q[i] for i in qids}))
    if ds == "trec-covid":
        for v, qs in trec_covid.query_variants().items():
            if v != "Q-q":
                out.append(("test", v, qs))
        nar = {qid: t["narrative"] for qid, t in trec_covid.topics(5).items()}
        out.append(("test", "narrative", nar))
    return out


def build():
    if PACK.exists():
        shutil.rmtree(PACK)
    (PACK / "runs").mkdir(parents=True)
    (PACK / "qrels").mkdir()
    manifest = {"datasets": {}, "note": "BM25 Pyserini flat top-100; không có qrels test"}
    vocab = Counter()
    for ds in ("trec-covid", "nfcorpus", "scifact", "scifact-open"):
        need = set()
        entries = _queries_for(ds)
        info = {"runs": [], "queries": []}
        for split, variant, qs in entries:
            write_jsonl(PACK / "queries" / f"{ds}__{split}__{variant}.jsonl", ({"qid": k, "text": v} for k, v in qs.items()))
            info["queries"].append(f"{ds}__{split}__{variant}")
            for t in qs.values():
                vocab.update(tokenize(t))
            if variant == "Q-q":
                src = RUNS / ds / split / "bm25.trec"
                run = read_run(src)
                for d in run.values():
                    need |= set(d)
                shutil.copy(src, PACK / "runs" / f"{ds}__{split}.trec")
                info["runs"].append(f"{ds}__{split}")
            if split in ("train", "dev"):
                q = load_qrels(ds, "train") if ds == "scifact" else load_qrels(ds, split)
                with open(PACK / "qrels" / f"{ds}__{split}.tsv", "w") as f:
                    for qid in qs:
                        for did, rel in q.get(qid, {}).items():
                            f.write(f"{qid}\t{did}\t{rel}\n")
                            need.add(did)
        docs = _docs(ds, need)
        for d in docs:
            vocab.update(tokenize(f'{d["title"]} {d["text"]} {d.get("meta", "")}'))
        write_jsonl(PACK / "corpus" / f"{ds}.jsonl", docs)
        info["n_docs"] = len(docs)
        manifest["datasets"][ds] = info
        print(f"{ds:13s} {len(docs):6d} bài", flush=True)
    words = [w for w, _ in vocab.most_common(VOCAB_MAX)]
    (PACK / "vocab.txt").write_text("\n".join(words), encoding="utf-8")
    manifest["vocab_size"] = len(words)
    code = PACK / "code"
    shutil.copytree(ROOT / "src", code / "src", ignore=shutil.ignore_patterns("__pycache__", "demo"))
    shutil.copy(ROOT / "requirements-kaggle.txt", code / "requirements-kaggle.txt")
    shutil.copy(ROOT / "configs" / "models.yaml", code / "models.yaml")
    from . import oov_impute
    if (oov_impute.SRC / "emb.npy").exists():       # có output BioWordVec từ Kaggle → thêm vector OOV suy từ ngữ cảnh
        manifest["emb_v2"] = oov_impute.build()
    (PACK / "PACK_MANIFEST.json").write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    return manifest


def refresh_code():
    """Chép lại code mới nhất vào gói (không dựng lại dữ liệu). Gọi trước MỌI lần upload để kernel không chạy code cũ."""
    code = PACK / "code"
    if code.exists():
        shutil.rmtree(code)
    shutil.copytree(ROOT / "src", code / "src", ignore=shutil.ignore_patterns("__pycache__", "demo"))
    shutil.copy(ROOT / "requirements-kaggle.txt", code / "requirements-kaggle.txt")
    shutil.copy(ROOT / "configs" / "models.yaml", code / "models.yaml")


def _docs(ds, need):
    if ds == "scifact-open":
        out = []
        for did, title, abstract in scifact_open.corpus_iter():
            if did in need:
                out.append({"docid": did, "title": title, "text": abstract})
        return out
    corpus = load_corpus(ds)
    meta = metadata.doc_meta() if ds == "trec-covid" else {}
    out = []
    for did in sorted(need):
        if did in corpus:
            d = {"docid": did, **corpus[did]}
            if ds == "trec-covid":
                d["meta"] = metadata.meta_line(meta.get(did))
            out.append(d)
    return out


if __name__ == "__main__":
    print(json.dumps(build()["vocab_size"]))
