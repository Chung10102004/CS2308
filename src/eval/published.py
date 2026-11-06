"""Mọi con số đã công bố dùng trong đồ án, kèm nguồn — bảng và hình sinh từ đây, không gõ tay.

nDCG@10 × 100, BM25 (Pyserini flat) top-100 → rerank. Đã kiểm với PDF ngày 2026-11-06.
"""

ABDALLAH = "Abdallah et al. 2025, How Good are LLM-based Rerankers? (EMNLP Findings), arXiv:2508.16757"
RANKGPT = "Sun et al. 2023, RankGPT (EMNLP), arXiv:2304.09542, Table 1"
PYSERINI = "Pyserini 2CR BEIR, https://castorini.github.io/pyserini/2cr/beir.html (truy cập 2026-11-06)"
MEDCPT = "Jin et al. 2023, MedCPT, arXiv:2307.00589, Table 1 (first-stage khác: MedCPT retriever)"

# (tên, nhóm/thế hệ, năm, {bộ: nDCG@10}, nguồn, ghi chú)
ABDALLAH_ROWS = [
    ("BM25", "Lexical", 1994, {"trec-covid": 59.47, "nfcorpus": 30.75, "scifact": 67.89}, ABDALLAH + ", Table 2/3", ""),
    ("monoBERT (340M)", "Cross-encoder", 2019, {"trec-covid": 70.01, "nfcorpus": 36.88, "scifact": 71.36}, ABDALLAH + ", Table 2", ""),
    ("bge-reranker-base", "Cross-encoder", 2023, {"trec-covid": 67.50, "nfcorpus": 31.10, "scifact": 70.60}, ABDALLAH + ", Table 2", ""),
    ("bge-reranker-large", "Cross-encoder", 2023, {"trec-covid": 74.30, "nfcorpus": 34.80, "scifact": 74.10}, ABDALLAH + ", Table 2", ""),
    ("bge-reranker-v2-m3", "Cross-encoder", 2024, {"trec-covid": 74.79, "nfcorpus": 33.84, "scifact": 73.48}, ABDALLAH + ", Table 2", "mốc tái lập E0"),
    ("mxbai-rerank-base", "Cross-encoder", 2024, {"trec-covid": 84.00, "nfcorpus": 35.64, "scifact": 72.33}, ABDALLAH + ", Table 2", ""),
    ("Cohere Rerank-v2", "Cross-encoder (API)", 2023, {"trec-covid": 81.81, "nfcorpus": 36.36, "scifact": 74.44}, ABDALLAH + ", Table 2", ""),
    ("MonoT5-base", "Seq2seq", 2020, {"trec-covid": 72.24, "nfcorpus": 34.81, "scifact": 73.14}, ABDALLAH + ", Table 2", ""),
    ("MonoT5-3B", "Seq2seq", 2020, {"trec-covid": 80.71, "nfcorpus": 38.97, "scifact": 76.57}, ABDALLAH + ", Table 2", ""),
    ("InRanker-3B", "Seq2seq", 2024, {"trec-covid": 81.75, "nfcorpus": 38.25, "scifact": 78.31}, ABDALLAH + ", Table 2", ""),
    ("RankGPT gpt-3.5-turbo", "LLM listwise", 2023, {"trec-covid": 76.67, "nfcorpus": 35.62, "scifact": 70.43}, ABDALLAH + ", Table 3; " + RANKGPT, ""),
    ("RankGPT gpt-4", "LLM listwise", 2023, {"trec-covid": 85.51, "nfcorpus": 38.47, "scifact": 74.95}, ABDALLAH + ", Table 3; " + RANKGPT, "gpt-4 chỉ xếp lại top-30 của gpt-3.5"),
    ("RankZephyr 7B", "LLM listwise", 2023, {"trec-covid": 80.70, "nfcorpus": 36.58, "scifact": 75.13}, ABDALLAH + ", Table 3", ""),
    ("ListT5-3B", "LLM listwise", 2024, {"trec-covid": 84.70, "nfcorpus": 37.70, "scifact": 77.00}, ABDALLAH + ", Table 3", ""),
    ("Setwise Flan-T5-XXL (bubblesort)", "LLM setwise", 2024, {"trec-covid": 76.8, "nfcorpus": 34.6, "scifact": 75.4}, ABDALLAH + ", Table 3", ""),
]

# Mốc tái lập E0: hệ thống của nhóm -> dòng công bố tương ứng
E0_ANCHORS = {
    "bm25": "BM25",
    "bge_v2_m3": "bge-reranker-v2-m3",
    "bge_base": "bge-reranker-base",
    "bge_large": "bge-reranker-large",
    "mxbai_base": "mxbai-rerank-base",
    "monot5_base": "MonoT5-base",
}
E0_TOL = {"bm25": 0.5, "default": 1.0}

PYSERINI_BM25_FLAT = {"trec-covid": 59.5, "nfcorpus": 32.2}  # 0,595 và 0,322 trên trang 2CR (làm tròn 3 chữ số)
PYSERINI_BM25_FLAT_R100 = {"trec-covid": 0.109, "nfcorpus": 0.246}

MEDCPT_ROWS = {"MedCPT (retriever + CE)": {"trec-covid": 70.9, "nfcorpus": 35.5, "scifact": 76.1}}

BEIR_HOLE10_TREC_COVID = {  # BEIR Table 4: Hole@10 (%) và nDCG@10 trước → sau khi chấm thêm 980 cặp
    "BM25": (6.4, 0.656, 0.668), "docT5query": (2.8, 0.713, 0.714), "ANCE": (14.4, 0.654, 0.735),
    "TAS-B": (31.8, 0.481, 0.555), "ColBERT": (12.4, 0.677, 0.735), "BM25+CE": (1.6, 0.757, 0.760),
}

SCIFACT_OPEN_STATS = {"claims": 279, "citation": 209, "pooling": 251, "total": 460, "pool_systems": 4}


def row(name):
    for r in ABDALLAH_ROWS:
        if r[0] == name:
            return r
    raise KeyError(name)
