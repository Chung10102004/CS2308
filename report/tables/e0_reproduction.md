| Hệ thống | Bộ | Nhóm chạy lại | Bài báo | Lệch | Ngưỡng | Đạt? |
|---|---|---:|---:|---:|---:|:---:|
| BM25 (Pyserini flat) | TREC-COVID | 59.47 | 59.47 | -0.0 | ±0.5 | ✓ |
| BM25 (Pyserini flat) | NFCorpus | 32.18 | 30.75 | 1.43 | ±0.5 | ✗ |
| BM25 (Pyserini flat) | SciFact | 67.89 | 67.89 | 0.0 | ±0.5 | ✓ |
| bge-reranker-v2-m3 | TREC-COVID | 78.57 | 74.79 | 3.78 | ±1.0 | ✗ |
| bge-reranker-v2-m3 | NFCorpus | 33.69 | 33.84 | -0.15 | ±1.0 | ✓ |
| bge-reranker-v2-m3 | SciFact | 73.99 | 73.48 | 0.51 | ±1.0 | ✓ |
| bge-reranker-base | TREC-COVID | 68.61 | 67.5 | 1.11 | ±1.0 | ✗ |
| bge-reranker-base | NFCorpus | 31.55 | 31.1 | 0.45 | ±1.0 | ✓ |
| bge-reranker-base | SciFact | 71.55 | 70.6 | 0.95 | ±1.0 | ✓ |
| bge-reranker-large | TREC-COVID | 74.23 | 74.3 | -0.07 | ±1.0 | ✓ |
| bge-reranker-large | NFCorpus | 33.83 | 34.8 | -0.97 | ±1.0 | ✓ |
| bge-reranker-large | SciFact | 74.2 | 74.1 | 0.1 | ±1.0 | ✓ |
| mxbai-rerank-base | TREC-COVID | 83.06 | 84.0 | -0.94 | ±1.0 | ✓ |
| mxbai-rerank-base | NFCorpus | 35.48 | 35.64 | -0.16 | ±1.0 | ✓ |
| mxbai-rerank-base | SciFact | 72.03 | 72.33 | -0.3 | ±1.0 | ✓ |
| MonoT5-base | TREC-COVID | 74.08 | 72.24 | 1.84 | ±1.0 | ✗ |
| MonoT5-base | NFCorpus | 35.06 | 34.81 | 0.25 | ±1.0 | ✓ |
| MonoT5-base | SciFact | 73.24 | 73.14 | 0.1 | ±1.0 | ✓ |

nDCG@10 × 100. Bài báo: Abdallah et al. 2025, How Good are LLM-based Rerankers? (EMNLP Findings), arXiv:2508.16757. BM25 NFCorpus của Pyserini 2CR là 32,2 (≠ 30,75 trong bài) — xem mục 10.3 của plan.
