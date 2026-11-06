"""Sinh hình cho tiểu luận/slide (PNG, nền sáng, in được) từ results/e*/ → report/figures/.

Màu theo vai trò (đã chạy validate_palette của skill dataviz): xám = số công bố, cam = dòng nhóm tái lập
(có trong bài báo), xanh = dòng mới của nhóm. Mọi hình có nhãn chữ trực tiếp nên không phụ thuộc màu.
"""
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.eval import published as PUB  # noqa: E402
from src.eval.systems import BY_ID, SYSTEMS  # noqa: E402
from src.utils.paths import REPORT, RESULTS  # noqa: E402

F = REPORT / "figures"
BEIR3 = ("trec-covid", "nfcorpus", "scifact")
DSN = {"trec-covid": "TREC-COVID", "nfcorpus": "NFCorpus", "scifact": "SciFact"}
C = {"pub": "#b9b8b2", "repro": "#eb6834", "new": "#2a78d6", "ink": "#0b0b0b", "ink2": "#52514e",
     "grid": "#e6e5e0", "surface": "#fcfcfb", "s1": "#2a78d6", "s2": "#eb6834"}

plt.rcParams.update({
    "figure.facecolor": C["surface"], "axes.facecolor": C["surface"], "savefig.facecolor": C["surface"],
    "axes.edgecolor": C["grid"], "axes.labelcolor": C["ink2"], "xtick.color": C["ink2"], "ytick.color": C["ink2"],
    "text.color": C["ink"], "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True,
    "grid.color": C["grid"], "grid.linewidth": 0.8, "axes.axisbelow": True, "font.size": 9,
    "axes.titlesize": 11, "axes.titleweight": "bold", "legend.frameon": False,
})


def load(p):
    p = RESULTS / p
    return json.loads(p.read_text()) if p.exists() else None


def save(fig, name):
    F.mkdir(parents=True, exist_ok=True)
    fig.savefig(F / name, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print("→", F / name)


def ours_rows(e1, ds):
    rows = []
    for s in SYSTEMS:
        m = (e1.get(ds) or {}).get(s.sid)
        if m:
            kind = "repro" if s.anchor else "new"
            rows.append((f"{s.label} [nhóm]", 100 * m["nDCG@10"], kind, 100 * (m.get("nDCG@10_sd") or 0)))
    return rows


def fig_ranking():
    e1 = load("e1/e1.json") or {}
    fig, axes = plt.subplots(1, 3, figsize=(15, 9.5), sharey=False)
    for ax, ds in zip(axes, BEIR3):
        rows = [(n, sc[ds], "pub", 0) for n, _, _, sc, _, _ in PUB.ABDALLAH_ROWS] + ours_rows(e1, ds)
        rows.sort(key=lambda r: r[1])
        y = np.arange(len(rows))
        # dot plot (không dùng cột vì trục không bắt đầu từ 0)
        for yi, r in zip(y, rows):
            if r[3]:
                ax.plot([r[1] - r[3], r[1] + r[3]], [yi, yi], color=C["ink2"], linewidth=1.2, zorder=2)
        ax.scatter([r[1] for r in rows], y, s=[70 if r[2] != "pub" else 42 for r in rows],
                   color=[C[r[2]] for r in rows], edgecolor=C["surface"], linewidth=1.5, zorder=3)
        ax.set_yticks(y, [r[0] for r in rows], fontsize=7.5)
        for t, r in zip(ax.get_yticklabels(), rows):
            t.set_color(C["ink"] if r[2] != "pub" else C["ink2"])
            t.set_fontweight("bold" if r[2] != "pub" else "normal")
        for yi, r in zip(y, rows):
            if r[2] != "pub":
                ax.text(r[1] + r[3] + 0.6, yi, f"{r[1]:.1f}", va="center", fontsize=7, color=C["ink"])
        lo = min(r[1] for r in rows)
        ax.set_xlim(max(0, lo - 8), max(r[1] for r in rows) + 4)
        ax.set_title(DSN[ds])
        ax.set_xlabel("nDCG@10 × 100")
        ax.grid(axis="y", visible=False)
    handles = [plt.Line2D([], [], marker="o", linestyle="", markersize=7, color=C[k]) for k in ("pub", "repro", "new")]
    fig.legend(handles, ["Đã công bố (Abdallah et al. 2025)", "Nhóm chạy lại (có trong bài báo)", "Nhóm chạy mới"],
               loc="upper center", ncol=3, bbox_to_anchor=(0.5, 1.02))
    fig.suptitle("Cùng BM25 top-100: reranker của nhóm đặt cạnh bảng công bố", y=1.06, fontsize=13, fontweight="bold")
    fig.tight_layout()
    save(fig, "fig_e1_ranking.png")


def fig_timeline():
    e1 = load("e1/e1.json") or {}
    fig, ax = plt.subplots(figsize=(8, 4.8))
    pts = [(yr, np.mean([sc[d] for d in BEIR3]), n, "pub") for n, _, yr, sc, _, _ in PUB.ABDALLAH_ROWS]
    for s in SYSTEMS:
        vals = [(e1.get(d) or {}).get(s.sid) for d in BEIR3]
        if all(vals):
            pts.append((s.year, 100 * np.mean([v["nDCG@10"] for v in vals]), s.label, "repro" if s.anchor else "new"))
    for kind, marker, lab in (("pub", "o", "Đã công bố"), ("repro", "s", "Nhóm chạy lại"), ("new", "D", "Nhóm chạy mới")):
        P = [p for p in pts if p[3] == kind]
        if P:
            ax.scatter([p[0] for p in P], [p[1] for p in P], s=46, marker=marker, color=C[kind], edgecolor=C["surface"],
                       linewidth=1.5, label=lab, zorder=3)
    for p in pts:
        if p[3] != "pub" or p[2] in ("BM25", "RankGPT gpt-4", "MonoT5-3B", "InRanker-3B"):
            ax.annotate(p[2], (p[0], p[1]), xytext=(5, 3), textcoords="offset points", fontsize=7,
                        color=C["ink"] if p[3] != "pub" else C["ink2"])
    ax.set_xlabel("Năm ra đời của phương pháp")
    ax.set_ylabel("nDCG@10 TB 3 bộ × 100")
    ax.set_title("Dòng thời gian phương pháp rerank")
    ax.legend(loc="lower right")
    save(fig, "fig_timeline.png")


def fig_scifact_open():
    e3 = load("e3/e3.json")
    if not e3:
        return
    rows = e3["scifact_open"]["intersection"]["systems"]
    if not rows:
        return
    items = sorted(rows.items(), key=lambda x: x[1]["open"])
    fig, ax = plt.subplots(figsize=(7.5, 0.42 * len(items) + 1.6))
    y = np.arange(len(items))
    for yi, (sid, v) in zip(y, items):
        ax.plot([100 * v["orig"], 100 * v["open"]], [yi, yi], color=C["grid"], linewidth=2.5, zorder=1)
    ax.scatter([100 * v["orig"] for _, v in items], y, color=C["s2"], s=56, zorder=3, label="Nhãn gốc SciFact", edgecolor=C["surface"], linewidth=1.5)
    ax.scatter([100 * v["open"] for _, v in items], y, color=C["s1"], s=56, zorder=3, label="Nhãn đã soát (SciFact-Open)", edgecolor=C["surface"], linewidth=1.5)
    for yi, (sid, v) in zip(y, items):
        ax.text(100 * max(v["orig"], v["open"]) + 0.6, yi, f"{100 * v['delta']:+.1f}", va="center", fontsize=7.5, color=C["ink2"])
    ax.set_yticks(y, [f"{sid} {BY_ID[sid].label}" for sid, _ in items])
    ax.grid(axis="y", visible=False)
    ax.set_xlabel("nDCG@10 × 100 (190 claim có bằng chứng ở cả hai bộ nhãn)")
    k = e3["scifact_open"]["intersection"].get("kendall")
    ax.set_title("Chấm bằng nhãn thiếu so với nhãn đã soát" + (f" — Kendall τ = {k['tau']:.2f}" if k else ""))
    ax.legend(loc="lower right")
    save(fig, "fig_e3_scifact_open.png")


def fig_rounds():
    e3 = load("e3/e3.json")
    if not e3:
        return
    lv = e3["trec_covid_rounds"]["levels"]
    xs = [float(k) for k in lv]
    t1 = [(lv[k].get("kendall") or {}).get("tau") for k in lv]
    t2 = [(lv[k].get("kendall_condensed") or {}).get("tau") for k in lv]
    if all(t is None for t in t1):
        return
    fig, ax = plt.subplots(figsize=(6.5, 4))
    ax.plot(xs, t1, marker="o", color=C["s1"], linewidth=2, markersize=8, label="nDCG@10")
    ax.plot(xs, t2, marker="s", color=C["s2"], linewidth=2, markersize=8, label="nDCG@10 condensed")
    for x, a, b in zip(xs, t1, t2):
        ax.annotate(f"{a:.2f}", (x, a), xytext=(0, 7), textcoords="offset points", ha="center", fontsize=7.5)
        ax.annotate(f"{b:.2f}", (x, b), xytext=(0, -13), textcoords="offset points", ha="center", fontsize=7.5)
    ax.set_xticks(xs, [f"≤ vòng {int(x)}\n({lv[k]['n_pairs']:,} cặp)".replace(",", ".") for x, k in zip(xs, lv)])
    ax.set_ylabel("Kendall τ so với nhãn đầy đủ")
    ax.set_ylim(min([t for t in t1 + t2 if t is not None] + [0]) - 0.1, 1.15)
    ax.set_title("TREC-COVID: thứ hạng hệ thống khi nhãn còn nông")
    ax.legend(loc="lower right")
    save(fig, "fig_e3_trec_covid_rounds.png")


def fig_pareto():
    e4 = load("e4/e4.json")
    if not e4:
        return
    pts = [(sid, v) for sid, v in e4.items() if v.get("mean_ndcg10_beir3") is not None and v.get("usd_per_1k") is not None]
    if len(pts) < 2:
        return
    fig, ax = plt.subplots(figsize=(7.5, 4.8))
    xmin = 1e-4
    for sid, v in pts:
        x = max(v["usd_per_1k"], xmin)
        kind = "repro" if BY_ID.get(sid) and BY_ID[sid].anchor else "new"
        size = 30 + (v.get("p95_ms") or 0) / 40
        ax.scatter(x, 100 * v["mean_ndcg10_beir3"], s=size, color=C[kind], edgecolor=C["surface"], linewidth=1.5, zorder=3)
        ax.annotate(f"{sid} {BY_ID[sid].label if sid in BY_ID else sid}", (x, 100 * v["mean_ndcg10_beir3"]),
                    xytext=(6, 3), textcoords="offset points", fontsize=7.5)
    ax.set_xscale("log")
    ax.set_xlabel(f"USD / 1.000 truy vấn (thang log; ≤ {xmin} vẽ tại {xmin})")
    ax.set_ylabel("nDCG@10 TB 3 bộ × 100")
    ax.set_title("Chi phí – chất lượng (kích thước điểm ∝ độ trễ p95)")
    save(fig, "fig_e4_pareto.png")


if __name__ == "__main__":
    fig_ranking()
    fig_timeline()
    fig_scifact_open()
    fig_rounds()
    fig_pareto()
