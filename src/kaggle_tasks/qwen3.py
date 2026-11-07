"""Qwen3-Reranker-4B (LLM mã nguồn mở, 2025) trên BM25 top-100 — zero-shot, chạy song song trên mọi GPU.

Cách chấm theo model card: prompt hệ thống "Judge whether the Document meets the requirements…", điểm = logit("yes")
− logit("no") ở token cuối. Instruction mặc định của model card (không chỉnh theo miền, để so công bằng).
Đầu vào tài liệu: "tiêu đề. abstract" như mọi reranker khác của nhóm; tài liệu cắt còn MAX_DOC token.
Ra: out/runs/<bộ>/<split>/qwen3_4b.trec (test 4 bộ + dev 2 bộ cho RRF), out/latency.jsonl
"""
import json
import os
import threading
from concurrent.futures import ThreadPoolExecutor

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from .common import SMOKE, TEST_SETS, Pack, Timer, doc_text, gpu_name, out_dir, write_run

MODEL = os.environ.get("QWEN_MODEL", "Qwen/Qwen3-Reranker-4B")
NAME = os.environ.get("QWEN_NAME", "qwen3_4b")
INSTRUCT = "Given a web search query, retrieve relevant passages that answer the query"
PREFIX = ('<|im_start|>system\nJudge whether the Document meets the requirements based on the Query and the Instruct '
          'provided. Note that the answer can only be "yes" or "no".<|im_end|>\n<|im_start|>user\n')
SUFFIX = "<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n"
MAX_DOC, BATCH = int(os.environ.get("QWEN_MAX_DOC", "512")), int(os.environ.get("QWEN_BATCH", "8"))
SETS = TEST_SETS + [("nfcorpus", "dev"), ("scifact", "dev")]


class Scorer:
    def __init__(self, device):
        self.dev = device
        self.tok = AutoTokenizer.from_pretrained(MODEL, padding_side="left")
        dtype = torch.float16 if device.startswith("cuda") else torch.float32
        self.model = AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype=dtype).to(device).eval()
        self.yes = self.tok.convert_tokens_to_ids("yes")
        self.no = self.tok.convert_tokens_to_ids("no")
        self.pre = self.tok.encode(PREFIX, add_special_tokens=False)
        self.suf = self.tok.encode(SUFFIX, add_special_tokens=False)

    def _ids(self, query, doc):
        d = self.tok.encode(doc, add_special_tokens=False)[:MAX_DOC]
        body = self.tok.encode(f"<Instruct>: {INSTRUCT}\n<Query>: {query}\n<Document>: ", add_special_tokens=False)
        return self.pre + body + d + self.suf

    @torch.inference_mode()
    def score(self, query, docs):
        seqs = [self._ids(query, d) for d in docs]
        order = sorted(range(len(seqs)), key=lambda i: -len(seqs[i]))
        out = [0.0] * len(seqs)
        for s in range(0, len(order), BATCH):
            idx = order[s:s + BATCH]
            L = max(len(seqs[i]) for i in idx)
            ids = torch.full((len(idx), L), self.tok.pad_token_id, dtype=torch.long)
            att = torch.zeros((len(idx), L), dtype=torch.long)
            for r, i in enumerate(idx):          # đệm bên trái để token cuối là token cần đọc
                ids[r, L - len(seqs[i]):] = torch.tensor(seqs[i])
                att[r, L - len(seqs[i]):] = 1
            logits = self.model(input_ids=ids.to(self.dev), attention_mask=att.to(self.dev)).logits[:, -1, :]
            sc = (logits[:, self.yes] - logits[:, self.no]).float().tolist()
            for i, v in zip(idx, sc):
                out[i] = v
        return out


def main():
    pack, out = Pack(), out_dir("qwen3")
    n = max(1, torch.cuda.device_count())
    devices = [f"cuda:{i}" for i in range(n)] if torch.cuda.is_available() else ["cpu"]
    scorers = [Scorer(d) for d in devices]
    lat = open(out / "latency.jsonl", "a")
    lock = threading.Lock()
    for ds, split in SETS:
        corpus, cand, queries = pack.corpus(ds), pack.run(ds, split), pack.queries(ds, split, "Q-q")
        items = [(q, t) for q, t in queries.items() if cand.get(q)]
        run = {}

        def work(k):
            sc_obj = scorers[k]
            for qid, qtext in items[k::len(scorers)]:
                dids = [d for d, _ in cand[qid]]
                with Timer() as t:
                    s = sc_obj.score(qtext, [doc_text(corpus[d]) for d in dids])
                with lock:
                    run[qid] = dict(zip(dids, s))
                    lat.write(json.dumps({"model": NAME, "ds": ds, "variant": NAME, "qid": qid, "n_docs": len(dids),
                                          "ms": round(t.ms, 2), "device": gpu_name(), "parallel_gpus": len(scorers)}) + "\n")

        with ThreadPoolExecutor(len(scorers)) as ex:
            list(ex.map(work, range(len(scorers))))
        write_run(out / "runs" / ds / split / f"{NAME}.trec", run, NAME)
        print(f"{NAME} {ds:13s} {split:5s} {len(run)} truy vấn", flush=True)
    lat.close()
    (out / f"DONE_{NAME}").write_text(json.dumps({"model": MODEL, "gpus": len(scorers), "device": gpu_name(), "smoke": SMOKE}))


if __name__ == "__main__":
    main()
