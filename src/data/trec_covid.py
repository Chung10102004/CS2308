"""Official NIST topics and cumulative, iteration-aware relevance judgments."""
import xml.etree.ElementTree as ET

from ..utils.paths import RAW
from . import beir_loader


def topics(round_number=5):
    path = RAW / "trec-covid" / f"topics-rnd{round_number}.xml"
    root = ET.parse(path).getroot()
    return {t.attrib["number"]: {child.tag: (child.text or "").strip() for child in t} for t in root.findall("topic")}


def query_variants():
    rows = topics(5)
    return {"Q-q": {q: t["question"] for q, t in rows.items()},
            "Q-kw": {q: t["query"] for q, t in rows.items()},
            "Q-qn": {q: t["question"] + " " + t["narrative"] for q, t in rows.items()}}


def check_beir_matches_question():
    rows = topics(5)
    queries = beir_loader.load_queries("trec-covid", "test")
    return {"n_topics": len(rows), "beir_equals_question": sum(queries.get(q) == t["question"] for q, t in rows.items())}


def full_qrels_round1_topics():
    keep = set(topics(1))
    return {q: docs for q, docs in beir_loader.load_qrels("trec-covid", "test").items() if q in keep}


def _judgments():
    path = RAW / "trec-covid/qrels-covid_d5_j0.5-5.txt"
    with path.open(encoding="utf-8") as f:
        for line in f:
            qid, iteration, did, rel = line.split()
            yield qid, float(iteration), did, int(rel)


def round_qrels(level):
    full = full_qrels_round1_topics()
    result = {q: {} for q in full}
    for qid, iteration, did, rel in _judgments():
        if iteration <= level and did in full.get(qid, {}):
            if did in result[qid] and result[qid][did] != rel:
                raise ValueError(f"Conflicting judgments for {qid}/{did}")
            result[qid][did] = rel
    return result


def rounds_report():
    full, shallow = full_qrels_round1_topics(), round_qrels(1)
    return {"n_judgments": sum(1 for _ in _judgments()), "n_topics_round1": len(full),
            "shallow_pairs": sum(map(len, shallow.values())),
            "shallow_relevant": sum(r > 0 for docs in shallow.values() for r in docs.values()),
            "full_pairs_round1_topics": sum(map(len, full.values())),
            "full_relevant_round1_topics": sum(r > 0 for docs in full.values() for r in docs.values())}


def download():
    import requests
    folder = RAW / "trec-covid"
    folder.mkdir(parents=True, exist_ok=True)
    for name in [f"topics-rnd{r}.xml" for r in range(1, 6)] + ["qrels-covid_d5_j0.5-5.txt"]:
        path = folder / name
        if not path.exists():
            response = requests.get(f"https://ir.nist.gov/trec-covid/data/{name}", timeout=60)
            response.raise_for_status()
            path.write_bytes(response.content)
