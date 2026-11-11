"""Metadata cho TREC-COVID (mục 4.5–4.6 của plan) — không dùng LLM, không cần kiểm tay.

- Tài liệu: CORD-19 metadata.csv (2020-07-16) theo cord_uid → journal, publish_time, source_x, pubmed_id;
  PubMed efetch theo pubmed_id → MeSH (descriptor, major) và publication types.
- Câu hỏi: PubMed Automatic Term Mapping (esearch → querytranslation) → các MeSH term của câu hỏi.
E-utilities không cần key (≤3 request/giây); có NCBI_API_KEY trong API.json thì dùng (≤10/giây).
"""
import csv
import json
import re
import sys
import time

import requests
from lxml import etree

from ..utils import secrets
from ..utils.cache import Cache
from ..utils.io import read_json, write_json
from ..utils.paths import PROC, RAW

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
CORD19_URL = "https://ai2-semanticscholar-cord-19.s3-us-west-2.amazonaws.com/2020-07-16/metadata.csv"
CORD19 = RAW / "cord19" / "metadata.csv"
OUT_DOCS = PROC / "trec-covid" / "doc_metadata.json"
OUT_TOPICS = PROC / "trec-covid" / "topic_mesh.json"


class _Eutils:
    def __init__(self):
        keys = secrets.load()
        self.params = {"tool": "biorerank"}
        if keys["NCBI_API_KEY"]:
            self.params["api_key"] = keys["NCBI_API_KEY"]
        if keys["NCBI_EMAIL"]:
            self.params["email"] = keys["NCBI_EMAIL"]
        self.delay = 0.11 if keys["NCBI_API_KEY"] else 0.35
        self.cache = Cache("eutils")
        self._last = 0.0

    def get(self, endpoint, **params):
        payload = {"endpoint": endpoint, **params}
        hit = self.cache.get(payload)
        if hit is not None:
            return hit
        for attempt in range(5):
            wait = self.delay - (time.time() - self._last)
            if wait > 0:
                time.sleep(wait)
            self._last = time.time()
            r = requests.get(EUTILS + endpoint, params={**self.params, **params}, timeout=60)
            if r.status_code == 200:
                self.cache.set(payload, r.text)
                return r.text
            time.sleep(2 ** attempt)
        r.raise_for_status()


def load_cord19(cord_uids: set) -> dict:
    csv.field_size_limit(sys.maxsize)
    out = {}
    with open(CORD19, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            uid = row["cord_uid"]
            if uid in cord_uids and uid not in out:
                year = (row.get("publish_time") or "")[:4]
                out[uid] = {
                    "journal": row.get("journal") or None,
                    "year": int(year) if year.isdigit() else None,
                    "source": row.get("source_x") or None,
                    "pubmed_id": (row.get("pubmed_id") or "").split(".")[0] or None,
                    "doi": row.get("doi") or None,
                }
    return out


def parse_pubmed_xml(xml_text: str) -> dict:
    root = etree.fromstring(xml_text.encode())
    out = {}
    for art in root.iter("PubmedArticle"):
        pmid = art.findtext(".//MedlineCitation/PMID")
        mesh = [{"descriptor": d.text, "ui": d.get("UI"), "major": d.get("MajorTopicYN") == "Y"}
                for d in art.iterfind(".//MeshHeadingList/MeshHeading/DescriptorName")]
        ptypes = [p.text for p in art.iterfind(".//PublicationTypeList/PublicationType")]
        out[pmid] = {"mesh": mesh, "pub_types": ptypes}
    return out


def fetch_pubmed(pmids: list, eu: _Eutils, batch: int = 200) -> dict:
    out = {}
    for i in range(0, len(pmids), batch):
        chunk = pmids[i:i + batch]
        xml = eu.get("efetch.fcgi", db="pubmed", id=",".join(chunk), retmode="xml")
        out.update(parse_pubmed_xml(xml))
        print(f"  efetch {min(i + batch, len(pmids))}/{len(pmids)}", flush=True)
    return out


MESH_TAG = re.compile(r'"([^"]+)"\[MeSH Terms\]')


def atm_mesh(text: str, eu: _Eutils) -> list:
    js = json.loads(eu.get("esearch.fcgi", db="pubmed", term=text, retmode="json", retmax=0))
    qt = js.get("esearchresult", {}).get("querytranslation", "")
    return sorted(set(m.lower() for m in MESH_TAG.findall(qt)))


def build(cord_uids: set):
    from . import trec_covid
    eu = _Eutils()
    docs = load_cord19(cord_uids)
    pmids = sorted({d["pubmed_id"] for d in docs.values() if d["pubmed_id"]})
    pm = fetch_pubmed(pmids, eu)
    for d in docs.values():
        info = pm.get(d["pubmed_id"] or "", {})
        d["mesh"] = info.get("mesh", [])
        d["pub_types"] = info.get("pub_types", [])
    write_json(OUT_DOCS, docs)
    topics = {qid: {"mesh": atm_mesh(t["question"], eu), "mesh_kw": atm_mesh(t["query"], eu)}
              for qid, t in trec_covid.topics(5).items()}
    write_json(OUT_TOPICS, topics)
    n = len(cord_uids)
    cov = {
        "n_docs": n,
        "in_cord19_metadata": len(docs),
        "has_pubmed_id": sum(bool(d["pubmed_id"]) for d in docs.values()),
        "has_mesh": sum(bool(d["mesh"]) for d in docs.values()),
        "has_pub_types": sum(bool(d["pub_types"]) for d in docs.values()),
        "has_journal": sum(bool(d["journal"]) for d in docs.values()),
        "has_year": sum(bool(d["year"]) for d in docs.values()),
        "topics_with_mesh": sum(bool(t["mesh"]) for t in topics.values()),
    }
    cov.update({f"pct_{k}": round(100 * v / n, 1) for k, v in cov.items() if k.startswith("has_") or k == "in_cord19_metadata"})
    return cov


def _load_built(path):
    """Thiếu file thì báo lỗi rõ ràng (không ngầm trả {} rồi chạy M1 như M0)."""
    if not path.exists():
        raise FileNotFoundError(f"Thiếu metadata đã dựng: {path} — chạy `make data` (scripts/prepare_data.py) trước.")
    return read_json(path)


def doc_meta() -> dict:
    return _load_built(OUT_DOCS)


def topic_mesh() -> dict:
    return _load_built(OUT_TOPICS)


def meta_line(m: dict | None) -> str:
    """Dòng metadata chèn trước abstract ở mức M1."""
    if not m:
        return ""
    parts = []
    if m.get("journal"):
        parts.append(f"[Journal: {m['journal']}]")
    if m.get("year"):
        parts.append(f"[Year: {m['year']}]")
    pt = [p for p in m.get("pub_types", []) if p != "Journal Article"]
    if pt:
        parts.append(f"[Type: {', '.join(pt[:3])}]")
    major = [x["descriptor"] for x in m.get("mesh", []) if x["major"]] or [x["descriptor"] for x in m.get("mesh", [])][:5]
    if major:
        parts.append(f"[MeSH: {', '.join(major[:6])}]")
    return " ".join(parts)
