"""R5 — GPT listwise kiểu RankGPT (Sun et al., 2023): cửa sổ 20, bước 10, trượt từ dưới lên trên top-100.

- Prompt hoán vị của RankGPT (nhiều lượt: mỗi đoạn một lượt user/assistant), đoạn văn cắt 300 từ như bản gốc.
- Khác bản gốc: đầu ra là JSON {"ranking": [id,...]} qua structured outputs (Responses API) để parse chắc chắn;
  ID thiếu được nối vào cuối theo thứ tự cũ, ID trùng/không hợp lệ bị bỏ.
- gpt_large chỉ xếp lại top-`rerank_depth` (30) của gpt_small — giống RankGPT gpt-4†.
Mọi lệnh gọi đi qua Cache (SQLite) và CostLogger.
"""
import asyncio
import json
import time
from dataclasses import dataclass

import tiktoken

from ..utils import secrets
from ..utils.cache import Cache
from ..utils.cost_logger import CallLog, CostLogger, Pricing

WINDOW, STEP, MAX_WORDS = 20, 10, 300
EST_OUTPUT_TOKENS = 130          # ~20 ID trong JSON
EST_REASONING_TOKENS = {"none": 0, "low": 300, "medium": 1200, "high": 4000}  # giả định cho dry-run

SCHEMA = {
    "type": "object",
    "properties": {"ranking": {"type": "array", "items": {"type": "integer"}}},
    "required": ["ranking"],
    "additionalProperties": False,
}


def windows(n: int, window: int = WINDOW, step: int = STEP):
    """Các cửa sổ (start, end) theo thứ tự xử lý của RankGPT: từ cuối danh sách lên đầu."""
    end = n
    start = max(0, end - window)
    out = []
    while True:
        out.append((start, end))
        if start == 0:
            break
        end -= step
        start = max(0, end - window)
    return out


def truncate(text: str, max_words: int = MAX_WORDS) -> str:
    return " ".join(text.split()[:max_words])


def build_messages(query: str, passages: list, criteria: str | None = None) -> list:
    n = len(passages)
    crit = f" A passage is relevant if: {criteria.strip()}" if criteria else ""
    msgs = [
        {"role": "system", "content": "You are RankGPT, an intelligent assistant that can rank passages based on their relevancy to the query."},
        {"role": "user", "content": f"I will provide you with {n} passages, each indicated by number identifier []. \nRank the passages based on their relevance to query: {query}.{crit}"},
        {"role": "assistant", "content": "Okay, please provide the passages."},
    ]
    for i, p in enumerate(passages, 1):
        msgs.append({"role": "user", "content": f"[{i}] {truncate(p)}"})
        msgs.append({"role": "assistant", "content": f"Received passage [{i}]."})
    msgs.append({"role": "user", "content": (
        f"Search Query: {query}. \nRank the {n} passages above based on their relevance to the search query. "
        "The passages should be listed in descending order using identifiers. The most relevant passages should be "
        'listed first. Return JSON {"ranking": [identifiers]} containing every identifier exactly once. '
        "Only respond with the ranking, do not say any word or explain.")})
    return msgs


def repair(perm: list, n: int) -> list:
    """Hoán vị 0-based hợp lệ từ đầu ra 1-based của model: bỏ trùng/ngoài khoảng, nối phần thiếu vào cuối."""
    seen, out = set(), []
    for x in perm:
        if isinstance(x, int) and 1 <= x <= n and x not in seen:
            seen.add(x)
            out.append(x - 1)
    out += [i for i in range(n) if i + 1 not in seen]
    return out


_ENC = None


def count_tokens(msgs: list) -> int:
    global _ENC
    if _ENC is None:
        _ENC = tiktoken.get_encoding("o200k_base")
    return sum(len(_ENC.encode(m["content"])) + 4 for m in msgs) + 3


@dataclass
class GPTConfig:
    model: str
    reasoning_effort: str = "none"
    rerank_depth: int = 100
    max_concurrency: int = 8


class GPTListwise:
    def __init__(self, cfg: GPTConfig, run_id: str, log_path, role="rerank", client=None):
        self.cfg, self.run_id, self.role = cfg, run_id, role
        self.cache = Cache("openai")
        self.logger = CostLogger(log_path)
        self.pricing = Pricing()
        self._client = client

    @property
    def client(self):
        if self._client is None:
            from openai import AsyncOpenAI
            self._client = AsyncOpenAI(api_key=secrets.get("OPENAI_API_KEY"), max_retries=6, timeout=180)
        return self._client

    def _payload(self, msgs):
        return {"model": self.cfg.model, "effort": self.cfg.reasoning_effort, "messages": msgs, "schema": SCHEMA}

    async def _call(self, qid, msgs, n):
        payload = self._payload(msgs)
        hit = self.cache.get(payload)
        if hit is not None:
            self.logger.log(CallLog(self.run_id, self.role, self.cfg.model, "listwise", qid, n, cache_hit=True))
            return hit["ranking"]
        t0 = time.perf_counter()
        kwargs = {"model": self.cfg.model, "input": msgs,
                  "text": {"format": {"type": "json_schema", "name": "ranking", "schema": SCHEMA, "strict": True}}}
        if self.cfg.reasoning_effort:
            kwargs["reasoning"] = {"effort": self.cfg.reasoning_effort}
        status, ranking, usage = "ok", [], None
        try:
            resp = await self.client.responses.create(**kwargs)
            usage = resp.usage
            ranking = json.loads(resp.output_text)["ranking"]
        except (json.JSONDecodeError, KeyError, TypeError):
            status = "parse_error"
        ms = (time.perf_counter() - t0) * 1000
        it = getattr(usage, "input_tokens", 0) or 0
        ot = getattr(usage, "output_tokens", 0) or 0
        cached = getattr(getattr(usage, "input_tokens_details", None), "cached_tokens", 0) or 0
        reas = getattr(getattr(usage, "output_tokens_details", None), "reasoning_tokens", 0) or 0
        cost = self.pricing.openai(self.cfg.model, it, ot, cached) or 0.0
        self.logger.log(CallLog(self.run_id, self.role, self.cfg.model, "listwise", qid, n, it, ot, 1, ms, cost,
                                False, status, 0, cached_input_tokens=cached, reasoning_tokens=reas))
        if status == "ok":
            self.cache.set(payload, {"ranking": ranking})
        return ranking

    async def rerank_query(self, qid, query, docids, texts, criteria=None):
        order = list(range(len(docids)))
        depth = min(self.cfg.rerank_depth, len(order))
        for s, e in windows(depth):
            idx = order[s:e]
            perm = repair(await self._call(qid, build_messages(query, [texts[i] for i in idx], criteria), len(idx)), len(idx))
            order[s:e] = [idx[p] for p in perm]
        return [docids[i] for i in order]

    async def rerank_all(self, items, criteria_for=None):
        """items: [(qid, query, docids, texts)] → {qid: [docid theo thứ tự mới]}."""
        sem = asyncio.Semaphore(self.cfg.max_concurrency)

        async def one(it):
            async with sem:
                return it[0], await self.rerank_query(*it, criteria=criteria_for(it[0]) if criteria_for else None)

        return dict(await asyncio.gather(*(one(it) for it in items)))

    def estimate(self, items, criteria_for=None) -> dict:
        """Ước tính không gọi API: token theo tiktoken, output theo hằng số, bỏ qua phần đã có trong cache."""
        calls = cached = it = 0
        for qid, query, docids, texts in items:
            depth = min(self.cfg.rerank_depth, len(docids))
            for s, e in windows(depth):
                msgs = build_messages(query, texts[s:e], criteria_for(qid) if criteria_for else None)   # thứ tự thật chỉ biết khi chạy; xấp xỉ bằng thứ tự BM25
                calls += 1
                if self.cache.get(self._payload(msgs)) is not None:
                    cached += 1
                    continue
                it += count_tokens(msgs)
        ot = (calls - cached) * (EST_OUTPUT_TOKENS + EST_REASONING_TOKENS.get(self.cfg.reasoning_effort, 0))
        usd = self.pricing.openai(self.cfg.model, it, ot) or 0.0
        return {"model": self.cfg.model, "calls": calls, "cached_calls": cached, "input_tokens": it,
                "output_tokens_est": ot, "usd": usd, "usd_batch": usd * self.pricing.cfg["openai"]["batch_discount"]}
