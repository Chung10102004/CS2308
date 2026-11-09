"""SciFact-Open evidence labels; provenance is retained, never inferred."""
import json
import tarfile

from ..utils.paths import RAW

URL = "https://scifact.s3.us-west-2.amazonaws.com/scifact-open/latest/scifact_open.tar.gz"


def claims():
    path = RAW / "scifact-open/claims.jsonl"
    with path.open(encoding="utf-8") as f:
        return {str(row["id"]): row for row in (json.loads(line) for line in f if line.strip())}


def queries():
    return {q: row["claim"] for q, row in claims().items()}


def qrels(scope="open"):
    if scope not in ("orig", "open"):
        raise ValueError("SciFact-Open qrels scope must be orig or open")
    out = {}
    for qid, row in claims().items():
        evidence = {str(did): 1 for did, label in row["evidence"].items() if scope == "open" or label["provenance"] == "citation"}
        if evidence:
            out[qid] = evidence
    return out


def corpus_iter():
    """Stream the entire original corpus, never a candidate-only subset."""
    path = RAW / "scifact-open/scifact_open.tar.gz"
    with tarfile.open(path, "r|gz") as archive:
        for member in archive:
            if member.name == "data/corpus.jsonl":
                for line in archive.extractfile(member):
                    row = json.loads(line)
                    abstract = row.get("abstract", [])
                    yield str(row["doc_id"]), row.get("title", ""), " ".join(abstract) if isinstance(abstract, list) else abstract
                return
    raise FileNotFoundError("data/corpus.jsonl missing from SciFact-Open archive")


def report():
    rows = claims()
    orig, opened = qrels("orig"), qrels("open")
    n_orig = sum(map(len, orig.values()))
    n_open = sum(map(len, opened.values()))
    return {"n_claims": len(rows), "evidence_citation": n_orig, "evidence_pooling": n_open - n_orig,
            "evidence_total": n_open, "claims_with_citation": len(orig), "claims_with_evidence": len(opened),
            "claims_with_added_evidence": sum(len(opened.get(q, {})) > len(orig.get(q, {})) for q in rows)}


def download():
    import requests
    folder = RAW / "scifact-open"
    folder.mkdir(parents=True, exist_ok=True)
    archive = folder / "scifact_open.tar.gz"
    if not archive.exists():
        partial = archive.with_suffix(".gz.part")
        with requests.get(URL, stream=True, timeout=(15, 180)) as response:
            response.raise_for_status()
            with partial.open("wb") as f:
                for chunk in response.iter_content(1024 * 1024):
                    f.write(chunk)
        partial.replace(archive)
    with tarfile.open(archive, "r:gz") as source:
        for name in ("claims.jsonl", "claims_metadata.jsonl"):
            target = folder / name
            if not target.exists():
                target.write_bytes(source.extractfile("data/" + name).read())
