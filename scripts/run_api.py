"""Chạy mọi thí nghiệm cần API (R5 GPT, R6 Jev). Mặc định chỉ ƯỚC TÍNH chi phí, không gọi API.

  python scripts/run_api.py --dry-run                 # bảng USD theo thí nghiệm (make api-dry)
  python scripts/run_api.py --confirm                 # chạy thật (make api-run CONFIRM=1)
  python scripts/run_api.py --only e1 --confirm       # chỉ một nhóm: e1 | e2 | e3 | e4
  python scripts/run_api.py --skip-large              # bỏ gpt_large (đắt nhất)
  python scripts/run_api.py --only e2 e3 e4 --systems gpt_small --dry-run
Mặc định chỉ chọn GPT-6 Luna và không chạy thật; cần --execute hoặc --confirm.
Kết quả: results/runs/<bộ>/<split>/<tên>.trec, log chi phí: results/api_logs/<tên>__<bộ>.jsonl
Chạy lại an toàn: mọi lệnh gọi đã xong nằm trong cache (data/cache/*.sqlite), không bị tính tiền lần hai.
"""
import argparse
import asyncio
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.rerank import candidates  # noqa: E402
from src.rerank.gpt_listwise import GPTConfig, GPTListwise  # noqa: E402
from src.rerank.jev import INSTRUCTIONS, JevRanker, narrative_instruction  # noqa: E402
from src.utils import cost_guard  # noqa: E402
from src.utils.cost_logger import CostLogger, Pricing  # noqa: E402
from src.utils.io import from_ranking, load_yaml, write_run  # noqa: E402
from src.utils.paths import RESULTS, RUNS  # noqa: E402

LOGS = RESULTS / "api_logs"
BEIR3 = ("trec-covid", "nfcorpus", "scifact")


@dataclass
class Job:
    exp: str
    system: str          # gpt_small | gpt_large | jev | jev_pw
    ds: str
    name: str            # tên run
    variant: str = "Q-q"
    meta: bool = False
    criteria: str = "generic"   # generic | narrative | medical
    depth: int = 100
    order_from: str | None = None
    shuffle_seed: int | None = None
    limit: int | None = None
    split: str = "test"


def crit_name(ds):
    return "narrative" if ds == "trec-covid" else "medical"


def jobs(skip_large=False):
    J = []
    # E1 — bảng chính
    for ds in BEIR3:
        J.append(Job("e1", "gpt_small", ds, "gpt_small"))
        if not skip_large:
            J.append(Job("e1", "gpt_large", ds, "gpt_large", order_from="gpt_small", depth=30))
        J.append(Job("e1", "jev", ds, "jev"))
    # E2 — tiêu chí 2×2, listwise vs pointwise, biến thể truy vấn/metadata, thiên vị vị trí
    for ds in BEIR3:
        J.append(Job("e2", "jev", ds, "jev.crit", criteria=crit_name(ds)))
        J.append(Job("e2", "gpt_small", ds, "gpt_small.crit", criteria=crit_name(ds)))
        J.append(Job("e2", "jev_pw", ds, "jev_pw"))
    for variant, meta in [("Q-kw", False), ("Q-qn", False), ("Q-q", True), ("Q-kw", True), ("Q-qn", True)]:
        suffix = ("" if variant == "Q-q" else f".{variant}") + (".M1" if meta else "")
        for sysname in ("gpt_small", "jev"):
            J.append(Job("e2", sysname, "trec-covid", sysname + suffix, variant=variant, meta=meta))
    for seed in (1, 2, 3):
        for sysname in ("gpt_small", "jev"):
            J.append(Job("e2", sysname, "trec-covid", f"{sysname}.shuf{seed}", shuffle_seed=seed))
            J.append(Job("e2", sysname, "nfcorpus", f"{sysname}.shuf{seed}", shuffle_seed=seed, limit=100))
    # E3 — nhãn thiếu trên SciFact-Open
    J.append(Job("e3", "gpt_small", "scifact-open", "gpt_small"))
    J.append(Job("e3", "jev", "scifact-open", "jev"))
    # E4 — cascade và quy mô k (100 câu NFCorpus cố định)
    for sysname in ("gpt_small", "jev"):
        J.append(Job("e4", sysname, "nfcorpus", f"cascade_bge_{sysname}20", order_from="bge_v2_m3", depth=20))
        for k in (10, 20, 50):
            J.append(Job("e4", sysname, "nfcorpus", f"{sysname}.k{k}", depth=k, limit=100))
    return J


def make_ranker(job: Job, models):
    log = LOGS / f"{job.name}__{job.ds}.jsonl"
    if job.system in ("gpt_small", "gpt_large"):
        m = models["openai"][job.system]
        cfg = GPTConfig(m["id"], m.get("reasoning_effort", "none"), job.depth if job.system == "gpt_small" else m.get("rerank_depth", job.depth))
        return GPTListwise(cfg, run_id=f"{job.name}__{job.ds}", log_path=log)
    mode = "pointwise" if job.system == "jev_pw" else "listwise"
    return JevRanker(f"{job.name}__{job.ds}", log, mode=mode, model=models["jev"]["model"],
                     split_state_budget=models["jev"]["split_state_budget"])


def instruction_for(job: Job):
    if job.criteria == "narrative":
        nar = candidates.narratives()
        return lambda qid: narrative_instruction(nar[qid])
    return lambda qid: INSTRUCTIONS[job.criteria]


def gpt_criteria_for(job: Job):
    if job.criteria == "generic":
        return None
    ins = instruction_for(job)
    return lambda qid: ins(qid)["criteria"]["true"]


def get_items(job: Job):
    if job.meta and not any(d.get("meta") for d in candidates.pack().corpus(job.ds).values()):
        raise FileNotFoundError(f"Missing document metadata for {job.ds}; refusing an M1 experiment with abstract-only input.")
    if job.order_from and not (RUNS / job.ds / job.split / f"{job.order_from}.trec").exists():
        return None
    return candidates.items(job.ds, job.split, job.variant, job.meta, job.depth, job.order_from, job.shuffle_seed, job.limit)


def estimate(job: Job, models):
    items = get_items(job)
    if items is None:
        # gpt_large phụ thuộc thứ tự của gpt_small: ước tính trên thứ tự BM25 (cùng số cửa sổ, cùng độ dài)
        items = candidates.items(job.ds, job.split, job.variant, job.meta, job.depth, None, job.shuffle_seed, job.limit)
    r = make_ranker(job, models)
    if isinstance(r, GPTListwise):
        return r.estimate(items, gpt_criteria_for(job))
    return r.estimate(items, instruction_for(job))


def run(job: Job, models):
    items = get_items(job)
    if items is None:
        print(f"  bỏ qua {job.name} ({job.ds}): chưa có run {job.order_from}")
        return False
    r = make_ranker(job, models)
    if isinstance(r, GPTListwise):
        out = asyncio.run(r.rerank_all(items, gpt_criteria_for(job)))
        run_ = {q: from_ranking(v) for q, v in out.items()}
    else:
        ins = instruction_for(job)
        run_ = {}
        for i, (qid, query, dids, texts) in enumerate(items, 1):
            run_[qid] = dict(zip(dids, r.rerank_query(qid, query, dids, texts, ins(qid))))
            if i % 25 == 0:
                print(f"    {i}/{len(items)}", flush=True)
    write_run(RUNS / job.ds / job.split / f"{job.name}.trec", run_, tag=job.name)
    s = CostLogger(LOGS / f"{job.name}__{job.ds}.jsonl").summary()
    print(f"  ✓ {job.exp} {job.name:24s} {job.ds:13s} {len(run_):4d} truy vấn | {s['requests']} request, {s['usd']:.3f} USD", flush=True)
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--execute", action="store_true", help="Chạy thật; mặc định chỉ ước tính")
    ap.add_argument("--systems", nargs="+", choices=["gpt_small", "gpt_large", "jev", "jev_pw"], default=["gpt_small"])
    ap.add_argument("--max-usd", type=float, help="Chặn trước khi chạy nếu ước tính vượt số USD này")
    ap.add_argument("--only", nargs="*", choices=["e1", "e2", "e3", "e4"])
    ap.add_argument("--skip-large", action="store_true")
    a = ap.parse_args()
    models = load_yaml("models.yaml")
    J = [j for j in jobs(a.skip_large) if j.system in a.systems and (not a.only or j.exp in a.only)]
    print(f"{'nhóm':4s} {'run':26s} {'bộ':13s} {'lệnh gọi':>8s} {'đã cache':>8s} {'USD':>8s}")
    total = 0.0
    by_exp = {}
    for j in J:
        e = estimate(j, models)
        total += e["usd"]
        by_exp[j.exp] = by_exp.get(j.exp, 0) + e["usd"]
        print(f"{j.exp:4s} {j.name:26s} {j.ds:13s} {e['calls']:8d} {e['cached_calls']:8d} {e['usd']:8.3f}")
    print("-" * 72)
    for k, v in by_exp.items():
        print(f"Tổng {k}: {v:.2f} USD")
    print(f"TỔNG ƯỚC TÍNH: {total:.2f} USD (giá: configs/pricing.yaml, ngày {Pricing().cfg['openai']['retrieved']})")
    print("Ghi chú: output/reasoning token của GPT và số request chia nhóm của Jev là ước lượng.")
    if a.dry_run or not (a.execute or a.confirm):
        print("Chỉ ước tính: chưa gọi API mô hình. Dùng --execute hoặc --confirm để chạy thật.")
        return
    if a.max_usd is not None and total > a.max_usd:
        raise cost_guard.BudgetExceeded(f"Ước tính {total:.2f} USD vượt --max-usd={a.max_usd:.2f}; chưa gọi API.")
    cost_guard.check(total, a.confirm, "run_api")
    for j in J:
        run(j, models)
    # gpt_large phụ thuộc gpt_small: chạy lại những job đã bị bỏ qua
    for j in J:
        if j.order_from and not (RUNS / j.ds / j.split / f"{j.name}.trec").exists():
            run(j, models)
    print("Xong. Chạy `make eval tables figures` để cập nhật bảng.")


if __name__ == "__main__":
    main()
