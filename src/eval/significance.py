"""Kiểm định ý nghĩa: paired bootstrap trên điểm từng truy vấn (Sakai 2006) và hiệu chỉnh Holm."""
import numpy as np


def paired_bootstrap(a: dict, b: dict, n: int = 10_000, seed: int = 0) -> dict:
    """a, b: qid -> điểm. Trả về delta = mean(a−b), p hai phía, khoảng tin cậy 95% của delta."""
    qids = sorted(set(a) & set(b))
    d = np.array([a[q] - b[q] for q in qids])
    if len(d) == 0:
        return {"delta": 0.0, "p": 1.0, "ci95": (0.0, 0.0), "n": 0}
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(d), size=(n, len(d)))
    boot = d[idx].mean(1)
    obs = d.mean()
    # kiểm định trên phân phối đã dời tâm về 0
    p = (np.sum(np.abs(boot - obs) >= abs(obs)) + 1) / (n + 1)
    lo, hi = np.percentile(boot, [2.5, 97.5])
    return {"delta": float(obs), "p": float(p), "ci95": (float(lo), float(hi)), "n": len(d)}


def mean_ci(x: dict, n: int = 10_000, seed: int = 0):
    v = np.array(list(x.values()))
    rng = np.random.default_rng(seed)
    boot = v[rng.integers(0, len(v), size=(n, len(v)))].mean(1)
    return float(v.mean()), tuple(float(t) for t in np.percentile(boot, [2.5, 97.5]))


def holm(pvals: list) -> list:
    """Hiệu chỉnh Holm–Bonferroni, giữ nguyên thứ tự đầu vào."""
    m = len(pvals)
    order = np.argsort(pvals)
    adj = [0.0] * m
    running = 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (m - rank) * pvals[i]))
        adj[i] = running
    return adj
