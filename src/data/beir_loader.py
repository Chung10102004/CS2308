"""Read original BEIR JSONL/TSV files, including the downloaded ZIP archives."""
import csv
import io
import json
import zipfile
from contextlib import contextmanager

from ..utils.paths import RAW


@contextmanager
def _reader(ds, name):
    path = RAW / "beir" / ds / name
    if path.exists():
        with path.open(encoding="utf-8-sig") as f:
            yield f
        return
    archive = RAW / "beir" / f"{ds}.zip"
    if not archive.exists():
        raise FileNotFoundError(f"Missing BEIR data: {path} or {archive}")
    with zipfile.ZipFile(archive) as z, z.open(f"{ds}/{name}") as raw:
        with io.TextIOWrapper(raw, encoding="utf-8-sig") as f:
            yield f


def load_corpus(ds):
    with _reader(ds, "corpus.jsonl") as f:
        out = {}
        for line in f:
            if line.strip():
                row = json.loads(line)
                out[str(row["_id"])] = {"title": row.get("title", ""), "text": row.get("text", "")}
        return out


def load_queries(ds, split=None):
    with _reader(ds, "queries.jsonl") as f:
        rows = [json.loads(line) for line in f if line.strip()]
    result = {str(r["_id"]): r["text"] for r in rows}
    if split is not None:
        keep = set(load_qrels(ds, split))
        result = {q: t for q, t in result.items() if q in keep}
    return result


def load_qrels(ds, split="test"):
    with _reader(ds, f"qrels/{split}.tsv") as f:
        out = {}
        for row in csv.DictReader(f, delimiter="\t"):
            out.setdefault(str(row["query-id"]), {})[str(row["corpus-id"])] = int(row["score"])
        return out


def doc_text(doc):
    title = (doc.get("title") or "").strip()
    text = (doc.get("text") or "").strip()
    return f"{title}. {text}" if title else text


def download():
    import requests
    folder = RAW / "beir"
    folder.mkdir(parents=True, exist_ok=True)
    for ds in ("trec-covid", "nfcorpus", "scifact"):
        path = folder / f"{ds}.zip"
        if path.exists() and zipfile.is_zipfile(path):
            continue
        url = f"https://public.ukp.informatik.tu-darmstadt.de/thakur/BEIR/datasets/{ds}.zip"
        temporary = path.with_suffix(".zip.part")
        with requests.get(url, stream=True, timeout=(15, 180)) as response:
            response.raise_for_status()
            with temporary.open("wb") as f:
                for chunk in response.iter_content(1024 * 1024):
                    f.write(chunk)
        if not zipfile.is_zipfile(temporary):
            raise ValueError(f"Invalid BEIR ZIP from {url}")
        temporary.replace(path)
