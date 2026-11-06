"""So thứ hạng hệ thống giữa hai bộ nhãn (E3): Kendall τ và số cặp hệ thống bị đảo thứ tự."""
from itertools import combinations

from scipy.stats import kendalltau


def kendall(scores_a: dict, scores_b: dict) -> dict:
    """scores_*: hệ thống -> điểm trung bình. Chỉ xét hệ thống có ở cả hai."""
    systems = sorted(set(scores_a) & set(scores_b))
    xa = [scores_a[s] for s in systems]
    xb = [scores_b[s] for s in systems]
    tau, p = kendalltau(xa, xb) if len(systems) > 1 else (float("nan"), float("nan"))
    swapped = [(s, t) for s, t in combinations(systems, 2)
               if (scores_a[s] - scores_a[t]) * (scores_b[s] - scores_b[t]) < 0]
    rank_a = {s: i + 1 for i, s in enumerate(sorted(systems, key=lambda s: -scores_a[s]))}
    rank_b = {s: i + 1 for i, s in enumerate(sorted(systems, key=lambda s: -scores_b[s]))}
    return {"n_systems": len(systems), "tau": float(tau), "p": float(p), "swapped_pairs": len(swapped),
            "swaps": swapped, "rank_a": rank_a, "rank_b": rank_b,
            "rank_change": {s: rank_a[s] - rank_b[s] for s in systems}}
