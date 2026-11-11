"""Topic của NIST (query/question/narrative) và qrels theo từng vòng của TREC-COVID.

Nguồn: https://ir.nist.gov/trec-covid/data.html
- topics-rnd{1..5}.xml: trường query (từ khóa), question (câu hỏi), narrative (mô tả mức liên quan)
- qrels-covid_d5_j0.5-5.txt: "topic iteration cord_uid judgment"; iteration = vòng chấm (có vòng lẻ 0.5, 1.5, …)
"""
import functools
import subprocess
from collections import defaultdict
from pathlib import Path

from lxml import etree

from ..utils.paths import RAW
from .beir_loader import load_corpus, load_qrels, load_queries

NIST = "https://ir.nist.gov/trec-covid/data/"
ROOT = RAW / "trec_covid"
QRELS_FILE = "qrels-covid_d5_j0.5-5.txt"


def download():
    ROOT.mkdir(parents=True, exist_ok=True)
    for f in [f"topics-rnd{r}.xml" for r in range(1, 6)] + [QRELS_FILE]:
        if not (ROOT / f).exists():
            subprocess.run(["curl", "-sSL", "-o", str(ROOT / f), NIST + f], check=True)


@functools.lru_cache(maxsize=None)
def topics(rnd: int = 5) -> dict:
    """qid -> {"query", "question", "narrative"}."""
    tree = etree.parse(str(ROOT / f"topics-rnd{rnd}.xml"))
    out = {}
    for t in tree.getroot().iter("topic"):
        out[t.get("number")] = {k: (t.findtext(k) or "").strip() for k in ("query", "question", "narrative")}
    return out


def query_variants() -> dict:
    """Ba dạng truy vấn của E2: Q-kw (từ khóa), Q-q (câu hỏi, mặc định BEIR), Q-qn (câu hỏi + narrative)."""
    t = topics(5)
    return {
        "Q-kw": {q: v["query"] for q, v in t.items()},
        "Q-q": {q: v["question"] for q, v in t.items()},
        "Q-qn": {q: f'{v["question"]} {v["narrative"]}' for q, v in t.items()},
    }


def check_beir_matches_question() -> dict:
    """Xác minh: truy vấn của BEIR TREC-COVID chính là trường `question` của NIST."""
    beir, t = load_queries("trec-covid"), topics(5)
    same = sum(beir.get(q, "").strip().lower() == v["question"].strip().lower() for q, v in t.items())
    return {"n_topics": len(t), "beir_equals_question": same}


@functools.lru_cache(maxsize=None)
def nist_qrels_with_rounds():
    """Danh sách (topic, iteration, docid, rel) theo đúng thứ tự file."""
    rows = []
    with open(ROOT / QRELS_FILE, encoding="utf-8") as f:
        for line in f:
            p = line.split()
            if len(p) == 4:
                rows.append((p[0], float(p[1]), p[2], int(p[3])))
    return rows


def round_qrels(max_iteration: float = 1.0) -> dict:
    """Nhãn nông: chỉ các cặp được chấm tới hết vòng `max_iteration`, trên các topic có từ vòng 1,
    giới hạn trong kho BEIR. Nếu một cặp được chấm lại thì lấy nhãn mới nhất trong phạm vi đó."""
    r1_topics = set(topics(1))
    corpus = load_corpus("trec-covid")
    q = defaultdict(dict)
    for topic, it, did, rel in sorted(nist_qrels_with_rounds(), key=lambda x: x[1]):
        if topic in r1_topics and it <= max_iteration and did in corpus:
            q[topic][did] = rel
    return dict(q)


def full_qrels_round1_topics() -> dict:
    """Nhãn đầy đủ (qrels test của BEIR) giới hạn trên các topic có từ vòng 1."""
    r1 = set(topics(1))
    return {qid: v for qid, v in load_qrels("trec-covid", "test").items() if qid in r1}


def rounds_report() -> dict:
    rows = nist_qrels_with_rounds()
    by_it = defaultdict(int)
    pairs = defaultdict(set)
    for topic, it, did, rel in rows:
        by_it[it] += 1
        pairs[(topic, did)].add(rel)
    rejudged = sum(1 for v in pairs.values() if len(v) > 1)
    shallow, full = round_qrels(1.0), full_qrels_round1_topics()
    return {
        "n_judgments": len(rows),
        "judgments_by_iteration": {str(k): v for k, v in sorted(by_it.items())},
        "n_topics_round1": len(topics(1)),
        "round1_topics": sorted(topics(1), key=int),
        "pairs_with_conflicting_labels": rejudged,
        "shallow_pairs": sum(len(v) for v in shallow.values()),
        "shallow_relevant": sum(r > 0 for v in shallow.values() for r in v.values()),
        "full_pairs_round1_topics": sum(len(v) for v in full.values()),
        "full_relevant_round1_topics": sum(r > 0 for v in full.values() for r in v.values()),
    }
