| | Hệ thống | Thế hệ | TREC-COVID | NFCorpus | SciFact | TB |
|---|---|---|---:|---:|---:|---:|
| công bố | BM25 | Lexical | 59.47 | 30.75 | 67.89 | 52.70 |
| công bố | monoBERT (340M) | Cross-encoder | 70.01 | 36.88 | 71.36 | 59.42 |
| công bố | bge-reranker-base | Cross-encoder | 67.50 | 31.10 | 70.60 | 56.40 |
| công bố | bge-reranker-large | Cross-encoder | 74.30 | 34.80 | 74.10 | 61.07 |
| công bố | bge-reranker-v2-m3 | Cross-encoder | 74.79 | 33.84 | 73.48 | 60.70 |
| công bố | mxbai-rerank-base | Cross-encoder | 84.00 | 35.64 | 72.33 | 63.99 |
| công bố | Cohere Rerank-v2 | Cross-encoder (API) | 81.81 | 36.36 | 74.44 | 64.20 |
| công bố | MonoT5-base | Seq2seq | 72.24 | 34.81 | 73.14 | 60.06 |
| công bố | MonoT5-3B | Seq2seq | 80.71 | 38.97 | 76.57 | 65.42 |
| công bố | InRanker-3B | Seq2seq | 81.75 | 38.25 | 78.31 | 66.10 |
| công bố | RankGPT gpt-3.5-turbo | LLM listwise | 76.67 | 35.62 | 70.43 | 60.91 |
| công bố | RankGPT gpt-4 | LLM listwise | 85.51 | 38.47 | 74.95 | 66.31 |
| công bố | RankZephyr 7B | LLM listwise | 80.70 | 36.58 | 75.13 | 64.14 |
| công bố | ListT5-3B | LLM listwise | 84.70 | 37.70 | 77.00 | 66.47 |
| công bố | Setwise Flan-T5-XXL (bubblesort) | LLM setwise | 76.80 | 34.60 | 75.40 | 62.27 |
| **nhóm** R0 | **BM25 (Pyserini flat)** | Lexical | **59.47** | **32.18** | **67.89** | **53.18** |
| **nhóm** R1 | **LambdaMART** | Learning-to-rank | **71.37 ± 2.59**† | **35.67 ± 0.07**† | **75.97 ± 0.37**† | **61.00** |
| **nhóm** R2 | **BiLSTM-ESIM** | LSTM | — | — | — | — |
| **nhóm** R3 | **MedCPT Cross-Encoder** | Cross-encoder (y sinh) | — | — | — | — |
| **nhóm** R4 | **bge-reranker-v2-m3** | Cross-encoder (tổng quát) | — | — | — | — |
| **nhóm** R5s | **GPT-6 Luna listwise** | LLM listwise | — | — | — | — |
| **nhóm** R5l | **GPT-6.1 Sol listwise (top-30)** | LLM listwise | — | — | — | — |
| **nhóm** R6 | **Jev listwise** | Mô hình quyết định | — | — | — | — |
| **nhóm** X1 | **bge-reranker-base** | Cross-encoder (tổng quát) | — | — | — | — |
| **nhóm** X2 | **bge-reranker-large** | Cross-encoder (tổng quát) | — | — | — | — |
| **nhóm** X3 | **mxbai-rerank-base** | Cross-encoder (tổng quát) | — | — | — | — |
| **nhóm** X4 | **MonoT5-base** | Seq2seq | — | — | — | — |

nDCG@10 × 100, cùng BM25 (Pyserini flat) top-100. Dòng *công bố*: Abdallah et al. 2025, How Good are LLM-based Rerankers? (EMNLP Findings), arXiv:2508.16757 (bảng 2–3). Dòng **nhóm**: số của nhóm; nhiều seed thì ghi trung bình ± SD (3 seed). † hơn BM25, ‡ hơn bge-reranker-v2-m3, ▾ kém bge-reranker-v2-m3 — paired bootstrap 10.000 lần, hiệu chỉnh Holm, p < 0,05. RankGPT gpt-4 và GPT-6.1 Sol của nhóm chỉ xếp lại top-30 của model nhỏ.
