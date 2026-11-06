"""Kiểm tra code API bằng client giả — không cần key, không tốn tiền."""
import asyncio
import json
from types import SimpleNamespace

import pytest

from src.rerank import gpt_listwise as G
from src.rerank import jev as J
from src.utils import cost_guard, secrets
from src.utils.cache import Cache


@pytest.fixture(autouse=True)
def tmp_cache(tmp_path, monkeypatch):
    monkeypatch.setattr("src.utils.cache.CACHE", tmp_path / "cache")
    monkeypatch.setattr(G, "Cache", lambda name: Cache(name, root=tmp_path / "cache"))
    monkeypatch.setattr(J, "Cache", lambda name: Cache(name, root=tmp_path / "cache"))
    return tmp_path


def test_windows_match_rankgpt():
    assert G.windows(100) == [(80, 100), (70, 90), (60, 80), (50, 70), (40, 60), (30, 50), (20, 40), (10, 30), (0, 20)]
    assert len(G.windows(100)) == 9
    assert G.windows(30) == [(10, 30), (0, 20)]
    assert G.windows(15) == [(0, 15)]


def test_repair_permutation():
    assert G.repair([3, 1, 2], 3) == [2, 0, 1]
    assert G.repair([2, 2, 9, 0], 3) == [1, 0, 2]          # trùng, ngoài khoảng → bỏ; thiếu → nối cuối
    assert G.repair([], 4) == [0, 1, 2, 3]


def test_messages_truncate_and_count():
    msgs = G.build_messages("q", ["w " * 500, "short"], criteria="about drugs")
    assert len(msgs[3]["content"].split()) == 301   # "[1]" + 300 từ
    assert "A passage is relevant if: about drugs" in msgs[1]["content"]
    assert G.count_tokens(msgs) > 300


class FakeResponses:
    """Giả lập Responses API: luôn đảo ngược thứ tự các đoạn."""

    def __init__(self):
        self.calls = 0

    async def create(self, model, input, text, reasoning=None):
        self.calls += 1
        n = sum(1 for m in input if m["role"] == "user" and m["content"].startswith("["))
        usage = SimpleNamespace(input_tokens=1000, output_tokens=50,
                                input_tokens_details=SimpleNamespace(cached_tokens=0),
                                output_tokens_details=SimpleNamespace(reasoning_tokens=0))
        return SimpleNamespace(output_text=json.dumps({"ranking": list(range(n, 0, -1))}), usage=usage)


def test_gpt_sliding_window_and_cache(tmp_path):
    fake = SimpleNamespace(responses=FakeResponses())
    r = G.GPTListwise(G.GPTConfig("gpt-6-luna", "none"), "t", tmp_path / "log.jsonl", client=fake)
    docids = [f"d{i}" for i in range(100)]
    items = [("q1", "query", docids, [f"text {i}" for i in range(100)])]
    out = asyncio.run(r.rerank_all(items))
    assert fake.responses.calls == 9
    assert sorted(out["q1"]) == sorted(docids) and len(out["q1"]) == 100
    asyncio.run(r.rerank_all(items))                 # lần 2: trúng cache hoàn toàn
    assert fake.responses.calls == 9
    s = r.logger.summary()
    assert s["cache_hits"] == 9 and s["requests"] == 9 and s["usd"] > 0


def test_gpt_estimate_counts_calls(tmp_path):
    r = G.GPTListwise(G.GPTConfig("gpt-6-luna", "none"), "t", tmp_path / "log.jsonl", client=object())
    e = r.estimate([("q", "query", [str(i) for i in range(100)], ["abc def"] * 100)])
    assert e["calls"] == 9 and e["usd"] > 0


class FakeJev:
    def __init__(self):
        self.calls = 0

    def rerank(self, query, texts, instruction, threshold, return_documents, detail):
        J.INSTRUCTIONS  # noqa
        self.calls += 1
        res = [{"document_index": i, "score": 1.0 / (i + 1)} for i in range(len(texts))]
        return {"results": res, "detail": {"usage": {"requests": 2, "input_tokens": 5000, "output_tokens": 0},
                                           "resolved_models": ["jev-1.14.0"]}}


def test_jev_wrapper_scores_and_cache(tmp_path):
    fake = FakeJev()
    r = J.JevRanker("t", tmp_path / "jev.jsonl", ranker=fake)
    sc = r.rerank_query("q", "query", ["a", "b", "c"], ["x", "y", "z"], J.INSTRUCTIONS["generic"])
    assert sc == [1.0, 0.5, pytest.approx(1 / 3)]
    r.rerank_query("q", "query", ["a", "b", "c"], ["x", "y", "z"], J.INSTRUCTIONS["generic"])
    assert fake.calls == 1
    s = r.logger.summary()
    assert s["requests"] == 2 and s["cache_hits"] == 1


def test_jev_instructions_valid():
    from jev_reranker.instructions import validate_instruction
    for ins in list(J.INSTRUCTIONS.values()) + [J.narrative_instruction("seeking studies of X")]:
        validate_instruction(ins, "listwise")
        validate_instruction(ins, "pointwise")


def test_cost_guard():
    cost_guard.check(1.0, False)
    with pytest.raises(cost_guard.BudgetExceeded):
        cost_guard.check(50.0, False)
    assert cost_guard.check(50.0, True)


def test_secrets_missing(tmp_path, monkeypatch):
    f = tmp_path / "API.json"
    f.write_text(json.dumps({"OPENAI_API_KEY": "", "TYPESAFE_API_KEY": ""}))
    monkeypatch.setattr(secrets, "API_FILE", f)
    for k in secrets.KNOWN:
        monkeypatch.delenv(k, raising=False)
    with pytest.raises(secrets.MissingKey, match="OPENAI_API_KEY"):
        secrets.get("OPENAI_API_KEY")
    assert secrets.status()["OPENAI_API_KEY"] is False
    f.write_text("{not json")
    with pytest.raises(secrets.MissingKey):
        secrets.load()
