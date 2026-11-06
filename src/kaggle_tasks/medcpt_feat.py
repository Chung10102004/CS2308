"""Đặc trưng MedCPT bi-encoder (tích vô hướng query–article) cho mọi ứng viên — dùng cho R1 LambdaMART.

Ra: out/feats/medcpt/<bộ>__<split>.tsv  (qid, docid, score)
"""
import json

import torch
from transformers import AutoModel, AutoTokenizer

from .common import Pack, gpu_name, out_dir

Q_ID, A_ID = "ncbi/MedCPT-Query-Encoder", "ncbi/MedCPT-Article-Encoder"


@torch.inference_mode()
def encode(model, tok, inputs, max_len, dev, bs=64, pairs=False):
    embs = []
    for i in range(0, len(inputs), bs):
        chunk = inputs[i:i + bs]
        if pairs:
            enc = tok([a for a, _ in chunk], [b for _, b in chunk], truncation=True, padding=True,
                      max_length=max_len, return_tensors="pt")
        else:
            enc = tok(chunk, truncation=True, padding=True, max_length=max_len, return_tensors="pt")
        embs.append(model(**enc.to(dev)).last_hidden_state[:, 0, :].float().cpu())
    return torch.cat(embs) if embs else torch.empty(0, 768)


def main():
    pack, out = Pack(), out_dir("medcpt_feat")
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    qtok, atok = AutoTokenizer.from_pretrained(Q_ID), AutoTokenizer.from_pretrained(A_ID)
    qm = AutoModel.from_pretrained(Q_ID).to(dev).eval()
    am = AutoModel.from_pretrained(A_ID).to(dev).eval()
    if dev == "cuda":
        qm, am = qm.half(), am.half()
    for ds, info in pack.manifest["datasets"].items():
        corpus = pack.corpus(ds)
        jobs = []
        for rname in info["runs"]:
            _, split = rname.split("__")
            cand, qs = pack.run(ds, split), pack.queries(ds, split, "Q-q")
            jobs.append((split, cand, qs, [q for q in qs if q in cand]))
        dids = sorted({d for _, cand, _, qids in jobs for q in qids for d, _ in cand[q]})
        A = encode(am, atok, [(corpus[d].get("title") or "", corpus[d].get("text") or "") for d in dids], 512, dev, pairs=True)
        pos = {d: i for i, d in enumerate(dids)}
        for split, cand, qs, qids in jobs:
            Q = encode(qm, qtok, [qs[q] for q in qids], 64, dev)
            p = out / "feats" / "medcpt" / f"{ds}__{split}.tsv"
            p.parent.mkdir(parents=True, exist_ok=True)
            with open(p, "w") as f:
                for qi, qid in enumerate(qids):
                    ds_ids = [d for d, _ in cand[qid]]
                    sc = (A[[pos[d] for d in ds_ids]] @ Q[qi]).tolist()
                    for d, s in zip(ds_ids, sc):
                        f.write(f"{qid}\t{d}\t{s:.5f}\n")
            print(f"{ds:13s} {split:5s} {len(qids)} truy vấn", flush=True)
    (out / "DONE_medcpt_feat").write_text(json.dumps({"device": gpu_name()}))


if __name__ == "__main__":
    main()
