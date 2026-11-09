import sys
from types import SimpleNamespace

import pytest

from scripts import run_api


def fake_estimate(job, models):
    return {"usd": 0.10, "calls": 1, "cached_calls": 0}


def test_cli_defaults_to_dry_run_and_luna_only(monkeypatch):
    estimated, executed = [], []
    monkeypatch.setattr(sys, "argv", ["run_api.py", "--only", "e1"])
    def estimate(job, models):
        estimated.append(job.system)
        return fake_estimate(job, models)
    monkeypatch.setattr(run_api, "estimate", estimate)
    monkeypatch.setattr(run_api, "run", lambda *args: executed.append(args))
    run_api.main()
    assert estimated == ["gpt_small"] * 3
    assert executed == []


def test_budget_limit_blocks_execution_before_any_call(monkeypatch):
    executed = []
    monkeypatch.setattr(sys, "argv", ["run_api.py", "--only", "e1", "--confirm", "--max-usd", "0.01"])
    monkeypatch.setattr(run_api, "estimate", fake_estimate)
    monkeypatch.setattr(run_api, "run", lambda *args: executed.append(args))
    with pytest.raises(run_api.cost_guard.BudgetExceeded):
        run_api.main()
    assert executed == []


def test_metadata_experiment_rejects_absent_metadata(monkeypatch):
    monkeypatch.setattr(run_api.candidates, "pack", lambda: SimpleNamespace(corpus=lambda ds: {"a": {"title": "A", "text": "Text"}}))
    with pytest.raises(FileNotFoundError, match="metadata"):
        run_api.get_items(run_api.Job("e2", "gpt_small", "trec-covid", "gpt_small.M1", meta=True))
