"""Load previously built metadata; absence is explicit, never fabricated."""
import json

from ..utils.paths import PROC


def _load(names, label):
    for name in names:
        path = PROC / "trec-covid" / name
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    raise FileNotFoundError(f"Missing {label} metadata under {PROC / 'trec-covid'}; restore the original processed files before rerunning metadata experiments.")


def doc_meta():
    return _load(("doc_meta.json", "metadata.json"), "document")


def topic_mesh():
    return _load(("topic_mesh.json",), "topic MeSH")
