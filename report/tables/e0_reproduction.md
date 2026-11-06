| Hệ thống | Bộ | Nhóm chạy lại | Bài báo | Lệch | Ngưỡng | Đạt? |
|---|---|---:|---:|---:|---:|:---:|
| BM25 (Pyserini flat) | TREC-COVID | 59.47 | 59.47 | -0.0 | ±0.5 | ✓ |
| BM25 (Pyserini flat) | NFCorpus | 32.18 | 30.75 | 1.43 | ±0.5 | ✗ |
| BM25 (Pyserini flat) | SciFact | 67.89 | 67.89 | 0.0 | ±0.5 | ✓ |
| bge-reranker-v2-m3 | TREC-COVID | — | 74.79 | — | ±— | — |
| bge-reranker-v2-m3 | NFCorpus | — | 33.84 | — | ±— | — |
| bge-reranker-v2-m3 | SciFact | — | 73.48 | — | ±— | — |
| bge-reranker-base | TREC-COVID | — | 67.5 | — | ±— | — |
| bge-reranker-base | NFCorpus | — | 31.1 | — | ±— | — |
| bge-reranker-base | SciFact | — | 70.6 | — | ±— | — |
| bge-reranker-large | TREC-COVID | — | 74.3 | — | ±— | — |
| bge-reranker-large | NFCorpus | — | 34.8 | — | ±— | — |
| bge-reranker-large | SciFact | — | 74.1 | — | ±— | — |
| mxbai-rerank-base | TREC-COVID | — | 84.0 | — | ±— | — |
| mxbai-rerank-base | NFCorpus | — | 35.64 | — | ±— | — |
| mxbai-rerank-base | SciFact | — | 72.33 | — | ±— | — |
| MonoT5-base | TREC-COVID | — | 72.24 | — | ±— | — |
| MonoT5-base | NFCorpus | — | 34.81 | — | ±— | — |
| MonoT5-base | SciFact | — | 73.14 | — | ±— | — |

nDCG@10 × 100. Bài báo: Abdallah et al. 2025, How Good are LLM-based Rerankers? (EMNLP Findings), arXiv:2508.16757. BM25 NFCorpus của Pyserini 2CR là 32,2 (≠ 30,75 trong bài) — xem mục 10.3 của plan.
