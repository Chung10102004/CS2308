"""R2 — BiLSTM-ESIM reranker (Chen et al., 2017) với embedding BioWordVec 200 chiều (cố định).

Kiến trúc: BiLSTM mã hóa (200/hướng) → soft alignment → [a; ã; a−ã; a⊙ã] → chiếu 200 + ReLU → BiLSTM tổng hợp
→ avg+max pool hai phía → MLP → điểm. Đầu vào: truy vấn (≤64 token), tiêu đề + abstract (≤256 token).
Huấn luyện: softmax listwise trên nhóm 1 bài đúng + 7 bài sai lấy từ BM25 top-100; Adam; early stopping theo
nDCG@10 trên dev (NFCorpus dev + 20% train SciFact). Seed 0/1/2.
Ra: out/runs/<bộ>/test/bilstm_s<seed>[.<biến thể>][.M1].trec, out/train_log_s<seed>.json, out/latency.jsonl
"""
import json
import os
import random
import re
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.nn.utils.rnn import pack_padded_sequence, pad_packed_sequence

from .common import (E2_VARIANTS, SMOKE, TEST_SETS, Pack, Timer, doc_text, gpu_name, ndcg10, out_dir, run_name,
                     write_run)

TOKEN = re.compile(r"[a-z0-9]+(?:[-'][a-z0-9]+)*")
QLEN, DLEN, GROUP, BATCH = 64, 256, 8, 16
EPOCHS = int(os.environ.get("BILSTM_EPOCHS", "8"))
PATIENCE = int(os.environ.get("BILSTM_PATIENCE", "2"))
LR, HIDDEN, DROPOUT = 4e-4, 200, 0.3
SEEDS = [int(s) for s in os.environ.get("BILSTM_SEEDS", "0,1,2").split(",")]
# v2 (chọn trên dev): TAG=bilstm2, EM=1 (kênh khớp từ chính xác), OOV=alacarte (vector OOV suy từ ngữ cảnh,
# data/kaggle_pack/emb_v2) và cho phép học tiếp vector OOV; ABLATION=1 chạy hai bản bỏ bớt (seed 0).
TAG = os.environ.get("BILSTM_TAG", "bilstm")
USE_EM = os.environ.get("BILSTM_EM", "0") == "1"
OOV_MODE = os.environ.get("BILSTM_OOV", "random")          # random | alacarte
OOV_TRAIN = os.environ.get("BILSTM_OOV_TRAIN", "0") == "1"
ABLATION = os.environ.get("BILSTM_ABLATION", "0") == "1"
DEV_RUNS = os.environ.get("BILSTM_DEV_RUNS", "0") == "1"
TRAIN_SETS = [("nfcorpus", "train"), ("scifact", "train")]
DEV_SETS = [("nfcorpus", "dev"), ("scifact", "dev")]


def find_emb() -> Path:
    from .common import find_pack
    try:
        v2 = find_pack() / "emb_v2"          # có cả vector gốc (found) lẫn vector suy ra (imputed)
        if (v2 / "emb.npy").exists():
            return v2
    except FileNotFoundError:
        pass
    env = os.environ.get("BIORERANK_EMB")
    roots = [Path(env)] if env else ([Path("/kaggle/input")] if Path("/kaggle/input").exists()
                                     else [Path(__file__).resolve().parents[2] / "results" / "kaggle"])
    for r in roots:
        for p in r.rglob("emb.npy"):
            return p.parent
    raise FileNotFoundError("Không tìm thấy emb.npy (output của task biowordvec_cut)")


class Vocab:
    def __init__(self, words):
        self.idx = {w: i + 2 for i, w in enumerate(words)}  # 0 = PAD, 1 = UNK

    def ids(self, text, maxlen):
        return [self.idx.get(t, 1) for t in TOKEN.findall(text.lower())][:maxlen] or [1]


class Embed(nn.Module):
    """Vector BioWordVec cố định; nếu oov_mask được truyền và OOV_TRAIN, các dòng OOV được học tiếp."""

    def __init__(self, emb: torch.Tensor, oov_mask: torch.Tensor | None = None):
        super().__init__()
        self.base = nn.Embedding.from_pretrained(emb, freeze=True, padding_idx=0)
        self.train_oov = oov_mask is not None and OOV_TRAIN
        if self.train_oov:
            self.register_buffer("mask", oov_mask)
            self.oov = nn.Embedding.from_pretrained(emb.clone(), freeze=False, padding_idx=0)

    def forward(self, x):
        e = self.base(x)
        if self.train_oov:
            e = torch.where(self.mask[x][..., None], self.oov(x), e)
        return e


class ESIM(nn.Module):
    def __init__(self, emb: torch.Tensor, hidden=HIDDEN, dropout=DROPOUT, oov_mask=None, use_em=False):
        super().__init__()
        self.emb = Embed(emb, oov_mask)
        self.use_em = use_em
        d = emb.shape[1] + (1 if use_em else 0)
        self.enc = nn.LSTM(d, hidden, batch_first=True, bidirectional=True)
        self.proj = nn.Sequential(nn.Linear(8 * hidden, hidden), nn.ReLU())
        self.comp = nn.LSTM(hidden, hidden, batch_first=True, bidirectional=True)
        self.mlp = nn.Sequential(nn.Dropout(dropout), nn.Linear(8 * hidden, hidden), nn.Tanh(),
                                 nn.Dropout(dropout), nn.Linear(hidden, 1))

    @staticmethod
    def _rnn(lstm, x, lens):
        packed = pack_padded_sequence(x, lens.cpu(), batch_first=True, enforce_sorted=False)
        y, _ = lstm(packed)
        y, _ = pad_packed_sequence(y, batch_first=True, total_length=x.shape[1])
        return y

    def forward(self, q, ql, d, dl):
        qm = (q != 0).float()
        dm = (d != 0).float()
        eq, ed = self.emb(q), self.emb(d)
        if self.use_em:   # kênh khớp từ chính xác: token có xuất hiện ở phía bên kia không (bỏ PAD/UNK)
            same = (q[:, :, None] == d[:, None, :]) & (q[:, :, None] > 1) & (d[:, None, :] > 1)
            eq = torch.cat([eq, same.any(2, keepdim=True).float()], -1)
            ed = torch.cat([ed, same.any(1)[..., None].float()], -1)
        a = self._rnn(self.enc, eq, ql)
        b = self._rnn(self.enc, ed, dl)
        e = a @ b.transpose(1, 2)
        a_t = F.softmax(e.masked_fill(dm[:, None, :] == 0, -1e4), dim=2) @ b
        b_t = F.softmax(e.transpose(1, 2).masked_fill(qm[:, None, :] == 0, -1e4), dim=2) @ a
        ma = self.proj(torch.cat([a, a_t, a - a_t, a * a_t], -1))
        mb = self.proj(torch.cat([b, b_t, b - b_t, b * b_t], -1))
        va, vb = self._rnn(self.comp, ma, ql), self._rnn(self.comp, mb, dl)

        def pool(v, m):
            avg = (v * m[..., None]).sum(1) / m.sum(1, keepdim=True).clamp(min=1)
            mx = v.masked_fill(m[..., None] == 0, -1e4).max(1).values
            return avg, mx

        a_avg, a_max = pool(va, qm)
        b_avg, b_max = pool(vb, dm)
        return self.mlp(torch.cat([a_avg, a_max, b_avg, b_max], -1)).squeeze(-1)


def pad(seqs, dev):
    L = max(len(s) for s in seqs)
    x = torch.zeros(len(seqs), L, dtype=torch.long)
    for i, s in enumerate(seqs):
        x[i, :len(s)] = torch.tensor(s)
    return x.to(dev), torch.tensor([len(s) for s in seqs])


class Data:
    def __init__(self, pack: Pack, vocab: Vocab):
        self.pack, self.vocab, self._d = pack, vocab, {}

    def doc_ids(self, ds, did, meta=False):
        k = (ds, did, meta)
        if k not in self._d:
            self._d[k] = self.vocab.ids(doc_text(self.pack.corpus(ds)[did], with_meta=meta), DLEN)
        return self._d[k]

    def train_groups(self, rng):
        groups = []
        for ds, split in TRAIN_SETS:
            qs, cand, qrels = self.pack.queries(ds, split), self.pack.run(ds, split), self.pack.qrels(ds, split)
            for qid, text in qs.items():
                pos = [d for d, r in qrels.get(qid, {}).items() if r > 0 and d in self.pack.corpus(ds)]
                neg = [d for d, _ in cand.get(qid, []) if qrels.get(qid, {}).get(d, 0) <= 0]
                if not pos or not neg:
                    continue
                for p in rng.sample(pos, min(2, len(pos))):
                    ns = rng.sample(neg, GROUP - 1) if len(neg) >= GROUP - 1 else rng.choices(neg, k=GROUP - 1)
                    groups.append((self.vocab.ids(text, QLEN), [self.doc_ids(ds, d) for d in [p] + ns]))
        rng.shuffle(groups)
        return groups


@torch.no_grad()
def rerank(model, data: Data, ds, split, variant="Q-q", meta=False, dev="cpu", lat=None, tag=""):
    model.eval()
    qs, cand = data.pack.queries(ds, split, variant), data.pack.run(ds, split)
    run = {}
    for qid, text in qs.items():
        dids = [d for d, _ in cand.get(qid, [])]
        if not dids:
            continue
        qi = data.vocab.ids(text, QLEN)
        with Timer() as t:
            scores = []
            for s in range(0, len(dids), 50):
                chunk = dids[s:s + 50]
                d, dl = pad([data.doc_ids(ds, x, meta) for x in chunk], dev)
                q, ql = pad([qi] * len(chunk), dev)
                scores += model(q, ql, d, dl).float().tolist()
            if dev == "cuda":
                torch.cuda.synchronize()
        run[qid] = dict(zip(dids, scores))
        if lat is not None:
            lat.write(json.dumps({"model": "bilstm", "ds": ds, "variant": tag, "qid": qid, "n_docs": len(dids),
                                  "ms": round(t.ms, 2), "device": gpu_name()}) + "\n")
    return run


def dev_score(model, data, dev):
    vals = []
    for ds, split in DEV_SETS:
        vals.append(ndcg10(data.pack.qrels(ds, split), rerank(model, data, ds, split, dev=dev)))
    return float(np.mean(vals)), vals


def train_one(seed, data: Data, emb, out: Path, dev, tag="bilstm", oov_mask=None, use_em=False):
    random.seed(seed), np.random.seed(seed), torch.manual_seed(seed)
    rng = random.Random(seed)
    model = ESIM(emb, oov_mask=oov_mask, use_em=use_em).to(dev)
    opt = torch.optim.Adam([p for p in model.parameters() if p.requires_grad], lr=LR)
    log = {"seed": seed, "tag": tag, "epochs": [], "config": {
        "QLEN": QLEN, "DLEN": DLEN, "GROUP": GROUP, "BATCH": BATCH, "LR": LR, "HIDDEN": HIDDEN, "DROPOUT": DROPOUT,
        "EPOCHS": EPOCHS, "PATIENCE": PATIENCE, "EM": use_em, "OOV": OOV_MODE,
        "OOV_TRAIN": bool(oov_mask is not None and OOV_TRAIN)}}
    best, best_state, bad = -1, None, 0
    for ep in range(EPOCHS if not SMOKE else 1):
        model.train()
        t0, groups, losses = time.time(), data.train_groups(rng), []
        if SMOKE:
            groups = groups[:64]
        for s in range(0, len(groups), BATCH):
            batch = groups[s:s + BATCH]
            q, ql = pad([g[0] for g in batch for _ in range(GROUP)], dev)
            d, dl = pad([x for g in batch for x in g[1]], dev)
            scores = model(q, ql, d, dl).view(len(batch), GROUP)
            loss = F.cross_entropy(scores, torch.zeros(len(batch), dtype=torch.long, device=dev))
            opt.zero_grad()
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 10.0)
            opt.step()
            losses.append(loss.item())
        score, parts = dev_score(model, data, dev)
        log["epochs"].append({"epoch": ep, "loss": float(np.mean(losses)), "dev_ndcg10": score,
                              "dev_parts": dict(zip([f"{a}__{b}" for a, b in DEV_SETS], parts)),
                              "n_groups": len(groups), "seconds": round(time.time() - t0)})
        print(f"seed {seed} epoch {ep}: loss {np.mean(losses):.4f} dev nDCG@10 {score:.4f} ({time.time() - t0:.0f}s)", flush=True)
        if score > best:
            best, bad = score, 0
            best_state = {k: v.detach().clone() for k, v in model.state_dict().items()}
        else:
            bad += 1
            if bad >= PATIENCE:
                break
    model.load_state_dict(best_state)
    log["best_dev_ndcg10"] = best
    (out / f"train_log_{tag}_s{seed}.json" if tag != "bilstm" else out / f"train_log_s{seed}.json").write_text(json.dumps(log, indent=1))
    return model


def load_emb(ed: Path, oov_mode: str):
    words = json.loads((ed / "words.json").read_text())
    vecs = np.load(ed / "emb.npy").astype(np.float32)
    found = np.load(ed / "found.npy") if (ed / "found.npy").exists() else np.abs(vecs).sum(1) > 0
    have = found | (np.load(ed / "imputed.npy") if oov_mode == "alacarte" and (ed / "imputed.npy").exists() else False)
    rng = np.random.default_rng(0)
    oov = rng.normal(0, 0.1, size=vecs.shape).astype(np.float32)
    vecs = np.where(have[:, None], vecs, oov)
    emb = torch.tensor(np.vstack([np.zeros((1, vecs.shape[1]), np.float32),
                                  rng.normal(0, 0.1, (1, vecs.shape[1])).astype(np.float32), vecs]))
    oov_mask = torch.tensor(np.concatenate([[False, True], ~found]))   # các dòng không có vector BioWordVec gốc
    return words, emb, oov_mask, {"vocab": len(words), "found": int(found.sum()), "with_vector": int(have.sum())}


def run_config(pack, out, dev, tag, seeds, oov_mode, use_em, lat_first=True):
    global OOV_MODE
    OOV_MODE = oov_mode
    words, emb, oov_mask, st = load_emb(find_emb(), oov_mode)
    data = Data(pack, Vocab(words))
    (out / f"emb_stats_{tag}.json").write_text(json.dumps({**st, "oov_mode": oov_mode, "em": use_em}))
    lat = open(out / "latency.jsonl", "a")
    for seed in seeds:
        model = train_one(seed, data, emb, out, dev, tag, oov_mask if (OOV_TRAIN or oov_mode == "alacarte") else None, use_em)
        jobs = [(ds, split, "Q-q", False) for ds, split in TEST_SETS] + [("trec-covid", "test", v, m) for v, m in E2_VARIANTS]
        if DEV_RUNS:
            jobs += [(ds, split, "Q-q", False) for ds, split in DEV_SETS]
        for ds, split, variant, meta in jobs:
            name = run_name(f"{tag}_s{seed}", variant, meta)
            run = rerank(model, data, ds, split, variant, meta, dev, lat if (seed == seeds[0] and lat_first) else None, name)
            write_run(out / "runs" / ds / split / f"{name}.trec", run, name)
        torch.save(model.state_dict(), out / f"{tag}_s{seed}.pt")
    lat.close()


def main():
    pack, out = Pack(), out_dir("bilstm")
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    if ABLATION:   # bỏ từng thành phần của v2, seed 0
        run_config(pack, out, dev, "bilstm2_noem", [SEEDS[0]], "alacarte", False, lat_first=False)
        run_config(pack, out, dev, "bilstm2_nooov", [SEEDS[0]], "random", True, lat_first=False)
    else:
        run_config(pack, out, dev, TAG, SEEDS, OOV_MODE, USE_EM)
    (out / f"DONE_{TAG if not ABLATION else 'ablation'}").write_text(json.dumps({"seeds": SEEDS, "device": gpu_name(), "smoke": SMOKE}))


if __name__ == "__main__":
    main()
