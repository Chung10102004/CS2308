"""Kiểm tra dữ liệu và metric (cần `make data bm25` chạy trước; bỏ qua nếu thiếu dữ liệu)."""
import pytest

from src.utils.paths import RAW, RUNS

pytestmark = pytest.mark.skipif(not ((RAW / "beir" / "scifact" / "corpus.jsonl").exists() or (RAW / "beir" / "scifact.zip").exists()), reason="chưa tải dữ liệu")


def test_trec_covid_question_is_beir_query():
    from src.data import trec_covid
    r = trec_covid.check_beir_matches_question()
    assert r == {"n_topics": 50, "beir_equals_question": 50}
    assert len(trec_covid.topics(1)) == 30


def test_scifact_open_counts():
    from src.data import scifact_open
    r = scifact_open.report()
    assert (r["n_claims"], r["evidence_citation"], r["evidence_pooling"], r["evidence_total"]) == (279, 209, 251, 460)


@pytest.mark.skipif(not (RUNS / "scifact" / "test" / "bm25.trec").exists(), reason="chưa chạy BM25")
def test_e0_bm25_matches_paper():
    from src.data.beir_loader import load_qrels
    from src.eval.ir_metrics import evaluate
    from src.eval.published import row
    from src.utils.io import read_run
    for ds in ("trec-covid", "scifact"):
        m = evaluate(load_qrels(ds, "test"), read_run(RUNS / ds / "test" / "bm25.trec"))
        assert abs(m["nDCG@10"] * 100 - row("BM25")[3][ds]) <= 0.5


def test_metrics_toy():
    from src.eval.ir_metrics import evaluate, per_query
    qrels = {"1": {"a": 1, "b": 0}, "2": {"c": 2}}
    run = {"1": {"a": 2.0, "b": 1.0}, "2": {"x": 1.0}}
    m = evaluate(qrels, run)
    assert m["nDCG@10"] == pytest.approx(0.5)
    assert per_query(qrels, run) == {"1": 1.0, "2": 0.0}


def test_significance_and_tau():
    from src.eval.rank_correlation import kendall
    from src.eval.significance import holm, paired_bootstrap
    a = {str(i): 0.5 + 0.01 * i for i in range(50)}
    b = {str(i): 0.5 for i in range(50)}
    p = paired_bootstrap(a, b, n=2000, seed=0)
    assert p["p"] < 0.05 and p["delta"] > 0
    assert holm([0.01, 0.04, 0.5]) == pytest.approx([0.03, 0.08, 0.5])
    t = kendall({"x": 3, "y": 2, "z": 1}, {"x": 3, "y": 1, "z": 2})
    assert t["n_systems"] == 3 and t["swapped_pairs"] == 1
