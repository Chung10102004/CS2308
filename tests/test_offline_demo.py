import pytest


def test_offline_demo_uses_saved_rankings_and_explicit_unknown_labels(monkeypatch):
    from src.demo import offline_app
    data = {"queries": {"q": "Question"}, "corpus": {"a": {"title": "A", "text": "Text A"}, "b": {"title": "B", "text": "Text B"}}, "qrels": {"q": {"a": 1}}, "before": {"q": {"a": 2, "b": 1}}, "after": {"q": {"b": 2, "a": 1}}, "scores": {"R0": {"q": .8}, "R5s": {"q": .9}}}
    monkeypatch.setattr(offline_app, "dataset_data", lambda ds: data)
    result = offline_app.demo_result("trec-covid", "q")
    assert [d["id"] for d in result["before"]] == ["a", "b"]
    assert [d["id"] for d in result["after"]] == ["b", "a"]
    assert result["after"][0]["relevance"] is None
    assert result["after"][0]["movement"] == 1
    assert result["scores"] == {"before": .8, "after": .9}
    assert result["api_calls"] == 0


def test_offline_demo_rejects_unknown_dataset():
    from src.demo import offline_app
    with pytest.raises(ValueError):
        offline_app.dataset_data("../../API.json")
