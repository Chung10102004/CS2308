"""R3 MedCPT-CE, R4 bge-reranker-v2-m3 và 4 reranker phụ (zero-shot) trên BM25 top-100.

Ra: out/runs/<bộ>/test/<model>[.<biến thể>][.M1].trec, out/latency.jsonl
Biến thể (E2, chỉ TREC-COVID, chỉ R3/R4): Q-kw, Q-qn (đổi truy vấn), M1 (chèn dòng metadata trước bài).
"""
import json
import os

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer, T5ForConditionalGeneration

from .common import E2_VARIANTS, SMOKE, TEST_SETS, Pack, Timer, doc_text, gpu_name, out_dir, run_name, write_run

MODELS = {  # tên: (HF id, kiểu, fp16?)
    "medcpt_ce": ("ncbi/MedCPT-Cross-Encoder", "ce", True),
    "bge_v2_m3": ("BAAI/bge-reranker-v2-m3", "ce", True),
    "bge_base": ("BAAI/bge-reranker-base", "ce", True),
    "bge_large": ("BAAI/bge-reranker-large", "ce", True),
    "mxbai_base": ("mixedbread-ai/mxbai-rerank-base-v1", "ce", False),   # DeBERTa-v3: fp16 dễ tràn số
    "monot5_base": ("castorini/monot5-base-msmarco", "monot5", False),  # T5: fp16 dễ tràn số
}
E2_MODELS = ("medcpt_ce", "bge_v2_m3")
MAX_LEN, BATCH = 512, int(os.environ.get("CE_BATCH", "32"))


class CrossEncoder:
    def __init__(self, hf_id, kind, fp16):
        self.kind = kind
        self.dev = "cuda" if torch.cuda.is_available() else "cpu"
        self.tok = AutoTokenizer.from_pretrained(hf_id)
        if kind == "monot5":
            self.model = T5ForConditionalGeneration.from_pretrained(hf_id)
            self.true_id = self.tok.convert_tokens_to_ids("▁true")
            self.false_id = self.tok.convert_tokens_to_ids("▁false")
        else:
            self.model = AutoModelForSequenceClassification.from_pretrained(hf_id)
        if fp16 and self.dev == "cuda":
            self.model = self.model.half()
        self.model.to(self.dev).eval()

    @torch.inference_mode()
    def score(self, query: str, docs: list) -> list:
        order = sorted(range(len(docs)), key=lambda i: -len(docs[i]))
        out = [0.0] * len(docs)
        for s in range(0, len(order), BATCH):
            idx = order[s:s + BATCH]
            if self.kind == "monot5":
                texts = [f"Query: {query} Document: {docs[i]} Relevant:" for i in idx]
                enc = self.tok(texts, truncation=True, max_length=MAX_LEN, padding=True, return_tensors="pt").to(self.dev)
                dec = torch.full((len(idx), 1), self.model.config.decoder_start_token_id, device=self.dev)
                logits = self.model(**enc, decoder_input_ids=dec).logits[:, 0, [self.false_id, self.true_id]]
                sc = torch.log_softmax(logits.float(), dim=-1)[:, 1]
            else:
                enc = self.tok([query] * len(idx), [docs[i] for i in idx], truncation="only_second",
                               max_length=MAX_LEN, padding=True, return_tensors="pt").to(self.dev)
                sc = self.model(**enc).logits.float().view(-1)
            for i, v in zip(idx, sc.tolist()):
                out[i] = v
        return out


def main():
    pack, out = Pack(), out_dir("crossenc")
    lat = open(out / "latency.jsonl", "a")
    gpu = gpu_name()
    only = os.environ.get("CE_MODELS")
    names = only.split(",") if only else list(MODELS)
    for name in names:
        hf_id, kind, fp16 = MODELS[name]
        ce = CrossEncoder(hf_id, kind, fp16)
        jobs = [(ds, split, "Q-q", False) for ds, split in TEST_SETS]
        if name in E2_MODELS:
            jobs += [("trec-covid", "test", v, m) for v, m in E2_VARIANTS]
        for ds, split, variant, meta in jobs:
            corpus, cand = pack.corpus(ds), pack.run(ds, split)
            queries = pack.queries(ds, split, variant)
            run = {}
            for qid, qtext in queries.items():
                dids = [d for d, _ in cand.get(qid, [])]
                if not dids:          # BM25 không trả về bài nào (vd. 15 truy vấn NFCorpus) → bỏ qua, tính 0 khi chấm
                    continue
                texts = [doc_text(corpus[d], with_meta=meta) for d in dids]
                if torch.cuda.is_available():
                    torch.cuda.synchronize()
                with Timer() as t:
                    sc = ce.score(qtext, texts)
                    if torch.cuda.is_available():
                        torch.cuda.synchronize()
                run[qid] = dict(zip(dids, sc))
                lat.write(json.dumps({"model": name, "ds": ds, "variant": run_name(name, variant, meta), "qid": qid,
                                      "n_docs": len(dids), "ms": round(t.ms, 2), "device": gpu}) + "\n")
            rn = run_name(name, variant, meta)
            write_run(out / "runs" / ds / split / f"{rn}.trec", run, rn)
            print(f"{name:12s} {ds:13s} {rn:22s} {len(run)} truy vấn", flush=True)
        del ce
        torch.cuda.empty_cache() if torch.cuda.is_available() else None
    lat.close()
    (out / "DONE_crossenc").write_text(json.dumps({"models": names, "smoke": SMOKE, "device": gpu}))


if __name__ == "__main__":
    main()
