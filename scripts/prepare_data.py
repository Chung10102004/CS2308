"""Tải dữ liệu thô (không cần đăng ký), chia tập, kiểm rò rỉ, metadata TREC-COVID (make data).

Nguồn: BEIR (trec-covid, nfcorpus, scifact), NIST TREC-COVID (topic + qrels theo vòng), SciFact gốc (để xác minh split),
SciFact-Open, CORD-19 metadata.csv (2020-07-16). Bước metadata gọi PubMed E-utilities (không cần key).
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.data import beir_loader, metadata, scifact_open, splits, trec_covid  # noqa: E402
from src.utils.io import read_run, write_json  # noqa: E402
from src.utils.paths import RAW, RESULTS, RUNS  # noqa: E402


def curl(url, dst: Path):
    if dst.exists():
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["curl", "-sSL", "-o", str(dst), url], check=True)


def download():
    beir_loader.download()
    trec_covid.download()
    scifact_open.download()
    curl(metadata.CORD19_URL, metadata.CORD19)
    orig = RAW / "scifact_orig"
    if not (orig / "data" / "claims_dev.jsonl").exists():
        curl("https://scifact.s3-us-west-2.amazonaws.com/release/latest/data.tar.gz", orig / "data.tar.gz")
        subprocess.run(["tar", "-xzf", str(orig / "data.tar.gz"), "-C", str(orig)], check=True)


def build_metadata():
    ids = set()
    for v in ("", ".Q-kw", ".Q-qn"):
        p = RUNS / "trec-covid" / "test" / f"bm25{v}.trec"
        if p.exists():
            for docs in read_run(p).values():
                ids |= set(docs)
    if not ids:
        raise SystemExit("Chạy `make bm25` trước `make metadata`.")
    cov = metadata.build(ids)
    write_json(RESULTS / "data_report" / "trec_covid_metadata_coverage.json", cov)
    print(json.dumps(cov, indent=1))


if __name__ == "__main__":
    step = sys.argv[1] if len(sys.argv) > 1 else "download"
    if step == "download":
        download()
        _, rep = splits.build()
        print(json.dumps({k: v for k, v in rep.items() if k != "dropped_examples"}, ensure_ascii=False, indent=1))
        print(json.dumps(trec_covid.check_beir_matches_question()))
        print(json.dumps(scifact_open.report(), ensure_ascii=False))
    elif step == "metadata":
        build_metadata()
