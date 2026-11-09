import json
import zipfile

import pytest


def test_beir_reads_archives_and_filters_queries_by_qrels(tmp_path, monkeypatch):
    from src.data import beir_loader as loader
    monkeypatch.setattr(loader, "RAW", tmp_path)
    folder = tmp_path / "beir"
    folder.mkdir()
    with zipfile.ZipFile(folder / "toy.zip", "w") as z:
        z.writestr("toy/corpus.jsonl", json.dumps({"_id": "d1", "title": "Title", "text": "Abstract"}) + "\n")
        z.writestr("toy/queries.jsonl", "\n".join(json.dumps({"_id": q, "text": q}) for q in ("q1", "q2")))
        z.writestr("toy/qrels/test.tsv", "query-id\tcorpus-id\tscore\nq2\td1\t2\n")
    assert loader.load_corpus("toy") == {"d1": {"title": "Title", "text": "Abstract"}}
    assert loader.load_queries("toy") == {"q1": "q1", "q2": "q2"}
    assert loader.load_queries("toy", "test") == {"q2": "q2"}
    assert loader.load_qrels("toy", "test") == {"q2": {"d1": 2}}
    assert loader.doc_text({"title": "Title", "text": "Abstract"}) == "Title. Abstract"


def test_nist_variants_use_official_fields(tmp_path, monkeypatch):
    from src.data import trec_covid
    monkeypatch.setattr(trec_covid, "RAW", tmp_path)
    d = tmp_path / "trec-covid"
    d.mkdir()
    (d / "topics-rnd5.xml").write_text('<topics><topic number="1"><query>keywords</query><question>A question?</question><narrative>Relevant evidence</narrative></topic></topics>', encoding="utf-8")
    v = trec_covid.query_variants()
    assert v["Q-q"] == {"1": "A question?"}
    assert v["Q-kw"] == {"1": "keywords"}
    assert v["Q-qn"] == {"1": "A question? Relevant evidence"}
    assert trec_covid.topics(5)["1"]["narrative"] == "Relevant evidence"


def test_scifact_open_keeps_provenance_and_excludes_unlabelled_claims(tmp_path, monkeypatch):
    from src.data import scifact_open
    monkeypatch.setattr(scifact_open, "RAW", tmp_path)
    d = tmp_path / "scifact-open"
    d.mkdir()
    rows = [{"id": 7, "claim": "Claim", "evidence": {"a": {"provenance": "citation"}, "b": {"provenance": "pooling"}}}, {"id": 8, "claim": "Unlabelled", "evidence": {}}]
    (d / "claims.jsonl").write_text("\n".join(map(json.dumps, rows)), encoding="utf-8")
    assert scifact_open.queries() == {"7": "Claim", "8": "Unlabelled"}
    assert scifact_open.qrels("orig") == {"7": {"a": 1}}
    assert scifact_open.qrels("open") == {"7": {"a": 1, "b": 1}}
    with pytest.raises(ValueError):
        scifact_open.qrels("unknown")


def test_missing_metadata_fails_explicitly(tmp_path, monkeypatch):
    from src.data import metadata
    monkeypatch.setattr(metadata, "PROC", tmp_path)
    with pytest.raises(FileNotFoundError, match="metadata"):
        metadata.doc_meta()
