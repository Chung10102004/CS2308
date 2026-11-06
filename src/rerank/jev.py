"""R6 — Jev (TypeSafe) qua thư viện jev-reranker: rerank(threshold=0), listwise hoặc pointwise.

Tiêu chí (mục 6.3 của plan) truyền qua `instruction` = {"instructions": "...{document}...`query`...", "criteria": {...}}.
Tokenizer mặc định của jev-reranker (google/embeddinggemma-300m) là repo bị khóa trên HF, nên dùng
length_fn ước lượng ~4 ký tự/token để chia nhóm; mọi số token để chia nhóm vì vậy là ƯỚC LƯỢNG
(usage thật lấy từ detail["usage"] do API trả về).
"""
import time

from ..utils import secrets
from ..utils.cache import Cache
from ..utils.cost_logger import CallLog, CostLogger, Pricing

INSTRUCTIONS = {
    "generic": {
        "instructions": "Is {document} relevant to `query`?",
        "criteria": {"true": "The passage is relevant to the query.",
                     "false": "The passage is not relevant to the query."},
    },
    "medical": {
        "instructions": ("You are screening PubMed abstracts for a biomedical search system. "
                         "Does {document} provide evidence relevant to `query`?"),
        "criteria": {
            "true": ("The abstract addresses the same entities as the query (disease, gene, drug, intervention, "
                     "population) and reports findings, definitions or facts relevant to it."),
            "false": ("The abstract is off-topic, only shares background terms, concerns a different entity or "
                      "population, or contains nothing relevant."),
        },
    },
}


def narrative_instruction(narrative: str) -> dict:
    """Tiêu chí lấy nguyên văn trường narrative của NIST (TREC-COVID)."""
    return {"instructions": "Is {document} relevant to the topic `query`?",
            "criteria": {"true": narrative.strip(), "false": "The abstract does not meet the description above."}}


def approx_len(s: str) -> int:
    return (len(s) + 3) // 4


class JevRanker:
    def __init__(self, run_id: str, log_path, mode="listwise", model="jev-latest", split_state_budget=26000,
                 ranker=None):
        self.mode, self.model, self.run_id = mode, model, run_id
        self.cache = Cache("jev")
        self.logger = CostLogger(log_path)
        self.pricing = Pricing()
        self.split_state_budget = split_state_budget
        self._ranker = ranker

    @property
    def ranker(self):
        if self._ranker is None:
            from jev_reranker import JevReranker
            self._ranker = JevReranker(self.model, mode=self.mode, api_key=secrets.get("TYPESAFE_API_KEY"),
                                       dotenv_path=None, split_state_budget=self.split_state_budget,
                                       length_fn=approx_len)
        return self._ranker

    def _payload(self, query, texts, instruction):
        return {"model": self.model, "mode": self.mode, "query": query, "docs": texts, "instruction": instruction}

    def rerank_query(self, qid, query, docids, texts, instruction):
        payload = self._payload(query, texts, instruction)
        hit = self.cache.get(payload)
        if hit is not None:
            self.logger.log(CallLog(self.run_id, "rerank", self.model, self.mode, qid, len(texts), cache_hit=True))
            return hit["scores"]
        t0 = time.perf_counter()
        status = "ok"
        try:
            res = self.ranker.rerank(query, texts, instruction=instruction, threshold=0.0,
                                     return_documents=False, detail=True)
        except Exception as e:  # lỗi API: ghi log rồi ném lại để người chạy biết
            self.logger.log(CallLog(self.run_id, "rerank", self.model, self.mode, qid, len(texts), status=f"error:{type(e).__name__}",
                                    latency_ms=(time.perf_counter() - t0) * 1000))
            raise
        ms = (time.perf_counter() - t0) * 1000
        scores = [0.0] * len(texts)
        for r in res["results"]:
            scores[r["document_index"]] = float(r["score"])
        usage = res.get("detail", {}).get("usage", {})
        it, ot, nreq = usage.get("input_tokens", 0), usage.get("output_tokens", 0), usage.get("requests", 1)
        models = res.get("detail", {}).get("resolved_models", [])
        self.logger.log(CallLog(self.run_id, "rerank", ",".join(models) or self.model, self.mode, qid, len(texts),
                                it, ot, nreq, ms, self.pricing.jev(it), False, status, usage.get("retries", 0)))
        self.cache.set(payload, {"scores": scores, "models": models, "usage": usage})
        return scores

    def estimate(self, items, instruction_for) -> dict:
        calls = cached = tokens = 0
        for qid, query, docids, texts in items:
            ins = instruction_for(qid)
            calls += 1
            if self.cache.get(self._payload(query, texts, ins)) is not None:
                cached += 1
                continue
            # listwise: mọi tài liệu + truy vấn + tiêu chí đi trong một (hoặc vài) request
            per = approx_len(query) + approx_len(ins["instructions"]) + sum(approx_len(v) for v in ins["criteria"].values())
            body = sum(min(approx_len(t), 4000) for t in texts)
            n_req = max(1, -(-body // self.split_state_budget)) if self.mode == "listwise" else len(texts)
            tokens += body + per * n_req
        return {"model": self.model, "mode": self.mode, "calls": calls, "cached_calls": cached,
                "input_tokens_est": tokens, "usd": self.pricing.jev(tokens)}
