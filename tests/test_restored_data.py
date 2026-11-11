"""Kiểm tra các bộ đọc dữ liệu gốc trong src/data trên dữ liệu giả (không cần tải dữ liệu thật)."""
import json

import pytest


@pytest.fixture
def fresh_caches():
    """Các hàm đọc có lru_cache: xóa trước và sau mỗi test để dữ liệu giả không lẫn sang test dùng dữ liệu thật."""
    from src.data import beir_loader, scifact_open, trec_covid
    fns = (beir_loader.load_corpus, beir_loader.load_queries, beir_loader.load_qrels, trec_covid.topics, scifact_open.claims)
    for f in fns:
        f.cache_clear()
    yield
    for f in fns:
        f.cache_clear()


def test_beir_reads_corpus_queries_qrels(tmp_path, monkeypatch, fresh_caches):
    from src.data import beir_loader as loader
    monkeypatch.setattr(loader, "RAW", tmp_path)
    folder = tmp_path / "beir" / "scifact"
    (folder / "qrels").mkdir(parents=True)
    (folder / "corpus.jsonl").write_text(json.dumps({"_id": "d1", "title": "Title", "text": "Abstract"}) + "\n", encoding="utf-8")
    (folder / "queries.jsonl").write_text("\n".join(json.dumps({"_id": q, "text": q}) for q in ("q1", "q2")), encoding="utf-8")
    (folder / "qrels" / "test.tsv").write_text("query-id\tcorpus-id\tscore\nq2\td1\t2\n", encoding="utf-8")
    assert loader.load_corpus("scifact") == {"d1": {"title": "Title", "text": "Abstract"}}
    assert loader.load_queries("scifact") == {"q1": "q1", "q2": "q2"}
    assert loader.load_qrels("scifact", "test") == {"q2": {"d1": 2}}
    assert loader.load_qrels("scifact", "dev") == {}
    assert loader.doc_text({"title": "Title", "text": "Abstract"}) == "Title. Abstract"


def test_nist_variants_use_official_fields(tmp_path, monkeypatch, fresh_caches):
    from src.data import trec_covid
    monkeypatch.setattr(trec_covid, "ROOT", tmp_path)
    (tmp_path / "topics-rnd5.xml").write_text('<topics><topic number="1"><query>keywords</query><question>A question?</question><narrative>Relevant evidence</narrative></topic></topics>', encoding="utf-8")
    v = trec_covid.query_variants()
    assert v["Q-q"] == {"1": "A question?"}
    assert v["Q-kw"] == {"1": "keywords"}
    assert v["Q-qn"] == {"1": "A question? Relevant evidence"}
    assert trec_covid.topics(5)["1"]["narrative"] == "Relevant evidence"


def test_scifact_open_keeps_provenance_and_excludes_unlabelled_claims(tmp_path, monkeypatch, fresh_caches):
    from src.data import scifact_open
    monkeypatch.setattr(scifact_open, "ROOT", tmp_path)
    (tmp_path / "data").mkdir()
    rows = [{"id": 7, "claim": "Claim", "evidence": {"a": {"provenance": "citation"}, "b": {"provenance": "pooling"}}}, {"id": 8, "claim": "Unlabelled", "evidence": {}}]
    (tmp_path / "data" / "claims.jsonl").write_text("\n".join(map(json.dumps, rows)), encoding="utf-8")
    assert scifact_open.queries() == {"7": "Claim", "8": "Unlabelled"}
    assert scifact_open.qrels("orig") == {"7": {"a": 1}}
    assert scifact_open.qrels("open") == {"7": {"a": 1, "b": 1}}
    with pytest.raises(ValueError):
        scifact_open.qrels("unknown")


def test_missing_metadata_fails_explicitly(tmp_path, monkeypatch):
    from src.data import metadata
    monkeypatch.setattr(metadata, "OUT_DOCS", tmp_path / "doc_metadata.json")
    monkeypatch.setattr(metadata, "OUT_TOPICS", tmp_path / "topic_mesh.json")
    with pytest.raises(FileNotFoundError, match="metadata"):
        metadata.doc_meta()
    with pytest.raises(FileNotFoundError, match="metadata"):
        metadata.topic_mesh()
