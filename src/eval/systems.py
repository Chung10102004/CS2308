"""Danh mục hệ thống của nhóm: ID, tên hiển thị, thế hệ, năm phương pháp, tên run (nhiều seed → nhiều run)."""
from dataclasses import dataclass, field

import json

from ..utils.io import read_run
from ..utils.paths import RESULTS, RUNS


def _bilstm_v2():
    """Biến thể BiLSTM v2 được chọn theo dev (scripts/select_bilstm.py); mặc định bản gộp."""
    p = RESULTS / "bilstm_selection.json"
    if p.exists():
        sel = json.loads(p.read_text())
        return sel["chosen"], sel["label"]
    return "bilstm2", "BiLSTM-ESIM v2"


@dataclass
class System:
    sid: str
    label: str
    gen: str
    year: int
    runs: list
    anchor: str | None = None          # dòng công bố tương ứng (để tái lập E0)
    main: bool = True                  # thuộc R0–R6 (False: reranker phụ chỉ dùng cho E0/E3)
    note: str = ""
    extra: dict = field(default_factory=dict)


SYSTEMS = [
    System("R0", "BM25 (Pyserini flat)", "Lexical", 1994, ["bm25"], anchor="BM25"),
    System("R1", "LambdaMART", "Learning-to-rank", 2010, ["lambdamart_s0", "lambdamart_s1", "lambdamart_s2"]),
    System("R2", "BiLSTM-ESIM", "LSTM", 2017, ["bilstm_s0", "bilstm_s1", "bilstm_s2"]),
    System("R2b", _bilstm_v2()[1], "LSTM", 2017, [f"{_bilstm_v2()[0]}_s{i}" for i in range(3)],
           note="biến thể v2 chọn theo dev (3 seed)"),
    System("R3", "MedCPT Cross-Encoder", "Cross-encoder (y sinh)", 2023, ["medcpt_ce"]),
    System("R4", "bge-reranker-v2-m3", "Cross-encoder (tổng quát)", 2024, ["bge_v2_m3"], anchor="bge-reranker-v2-m3"),
    System("R5s", "GPT-6 Luna listwise", "LLM listwise", 2026, ["gpt_small"]),
    System("R5l", "GPT-6.1 Sol listwise (top-30)", "LLM listwise", 2026, ["gpt_large"], note="xếp lại top-30 của R5s, như RankGPT gpt-4"),
    System("R6", "Jev listwise", "Mô hình quyết định", 2026, ["jev"]),
    System("R7", "Qwen3-Reranker-4B", "LLM (mã nguồn mở)", 2025, ["qwen3_4b"]),
    System("R8", "RRF ensemble (chọn trên dev)", "Ensemble", 2009, ["rrf_dev"], note="tổ hợp các reranker zero-shot"),
    System("X1", "bge-reranker-base", "Cross-encoder (tổng quát)", 2023, ["bge_base"], anchor="bge-reranker-base", main=False),
    System("X2", "bge-reranker-large", "Cross-encoder (tổng quát)", 2023, ["bge_large"], anchor="bge-reranker-large", main=False),
    System("X3", "mxbai-rerank-base", "Cross-encoder (tổng quát)", 2024, ["mxbai_base"], anchor="mxbai-rerank-base", main=False),
    System("X4", "MonoT5-base", "Seq2seq", 2020, ["monot5_base"], anchor="MonoT5-base", main=False),
]
BY_ID = {s.sid: s for s in SYSTEMS}


def run_names(s: System, suffix: str = "") -> list:
    return [r + suffix for r in s.runs]


def available(s: System, ds: str, split: str = "test", suffix: str = "") -> list:
    return [RUNS / ds / split / f"{n}.trec" for n in run_names(s, suffix) if (RUNS / ds / split / f"{n}.trec").exists()]


def load_runs(s: System, ds: str, split="test", suffix=""):
    return [read_run(p) for p in available(s, ds, split, suffix)]
