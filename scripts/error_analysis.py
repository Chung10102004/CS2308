"""Ca tốt / ca không tốt (yêu cầu 5 của môn): truy vấn mà mỗi reranker hơn/kém BM25 nhiều nhất,
cộng các ca bất đồng giữa hai hệ thống → report/tables/error_cases.md và results/error_analysis.json.
Chạy sau `make eval` (đọc results/e1/e1_per_query.json)."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.data.beir_loader import load_corpus, load_qrels, load_queries  # noqa: E402
from src.eval.systems import BY_ID  # noqa: E402
from src.utils.io import ranking, read_run, write_json  # noqa: E402
from src.utils.paths import REPORT, RESULTS, RUNS  # noqa: E402

BEIR3 = ("trec-covid", "nfcorpus", "scifact")
K = 3


def top_doc(ds, run_name, qid):
    p = RUNS / ds / "test" / f"{run_name}.trec"
    if not p.exists():
        return None
    r = read_run(p).get(qid)
    return ranking(r)[0] if r else None


def main():
    pq = json.loads((RESULTS / "e1" / "e1_per_query.json").read_text())
    out, md = {}, ["# Ca tốt / ca không tốt (so với BM25, nDCG@10 từng truy vấn)\n"]
    for ds in BEIR3:
        Q, C, qrels = load_queries(ds), load_corpus(ds), load_qrels(ds, "test")
        base = pq[ds].get("R0")
        if not base:
            continue
        for sid, scores in pq[ds].items():
            if sid == "R0" or not scores:
                continue
            delta = sorted(((scores[q] - base[q], q) for q in scores if q in base), reverse=True)
            wins, losses = delta[:K], delta[-K:][::-1]
            out.setdefault(ds, {})[sid] = {"wins": wins, "losses": losses,
                                           "n_better": sum(d > 0 for d, _ in delta), "n_worse": sum(d < 0 for d, _ in delta),
                                           "n_same": sum(d == 0 for d, _ in delta)}
            md.append(f"## {ds} — {sid} {BY_ID[sid].label}: hơn BM25 ở {out[ds][sid]['n_better']} truy vấn, "
                      f"kém ở {out[ds][sid]['n_worse']}, bằng ở {out[ds][sid]['n_same']}\n")
            md.append("| Loại | Truy vấn | Δ nDCG@10 | Bài đầu của BM25 | Bài đầu của reranker |\n|---|---|---:|---|---|")
            run_name = BY_ID[sid].runs[0]
            for kind, rows in (("tốt", wins), ("không tốt", losses)):
                for d, q in rows:
                    b, r = top_doc(ds, "bm25", q), top_doc(ds, run_name, q)

                    def fmt(did):
                        if not did:
                            return "—"
                        rel = qrels.get(q, {}).get(did)
                        tag = "✓" if rel and rel > 0 else ("✗" if rel == 0 else "?")
                        return f"{tag} {C[did]['title'][:60]}"
                    md.append(f"| {kind} | {Q[q][:70]} | {100 * d:+.1f} | {fmt(b)} | {fmt(r)} |")
            md.append("")
    md.append("✓ = bài có nhãn liên quan, ✗ = có nhãn không liên quan, ? = chưa có nhãn.")
    write_json(RESULTS / "error_analysis.json", out)
    (REPORT / "tables").mkdir(parents=True, exist_ok=True)
    (REPORT / "tables" / "error_cases.md").write_text("\n".join(md), encoding="utf-8")
    print("→ report/tables/error_cases.md")


if __name__ == "__main__":
    main()
