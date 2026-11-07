| Hệ thống | Bộ | Bài báo | Nhóm: tiêu đề + abstract | Lệch | Đạt? | Nhóm: chỉ abstract, fp32 (như Rankify) | Lệch | Đạt? |
|---|---|---:|---:|---:|:---:|---:|---:|:---:|
| BM25 (Pyserini flat) | TREC-COVID | 59.47 | 59.47 | -0.0 | ✓ | — | — | — |
| BM25 (Pyserini flat) | NFCorpus | 30.75 | 32.18 | 1.43 | ✗ | — | — | — |
| BM25 (Pyserini flat) | SciFact | 67.89 | 67.89 | 0.0 | ✓ | — | — | — |
| bge-reranker-v2-m3 | TREC-COVID | 74.79 | 78.57 | 3.78 | ✗ | 74.26 | -0.53 | ✓ |
| bge-reranker-v2-m3 | NFCorpus | 33.84 | 33.69 | -0.15 | ✓ | 32.82 | -1.02 | ✗ |
| bge-reranker-v2-m3 | SciFact | 73.48 | 73.99 | 0.51 | ✓ | 71.39 | -2.09 | ✗ |
| bge-reranker-base | TREC-COVID | 67.5 | 68.61 | 1.11 | ✗ | 65.5 | -2.0 | ✗ |
| bge-reranker-base | NFCorpus | 31.1 | 31.55 | 0.45 | ✓ | 30.25 | -0.85 | ✓ |
| bge-reranker-base | SciFact | 70.6 | 71.55 | 0.95 | ✓ | 67.36 | -3.24 | ✗ |
| bge-reranker-large | TREC-COVID | 74.3 | 74.23 | -0.07 | ✓ | 71.57 | -2.73 | ✗ |
| bge-reranker-large | NFCorpus | 34.8 | 33.83 | -0.97 | ✓ | 32.79 | -2.01 | ✗ |
| bge-reranker-large | SciFact | 74.1 | 74.2 | 0.1 | ✓ | 71.31 | -2.79 | ✗ |
| mxbai-rerank-base | TREC-COVID | 84.0 | 83.06 | -0.94 | ✓ | 81.9 | -2.1 | ✗ |
| mxbai-rerank-base | NFCorpus | 35.64 | 35.48 | -0.16 | ✓ | 35.27 | -0.37 | ✓ |
| mxbai-rerank-base | SciFact | 72.33 | 72.03 | -0.3 | ✓ | 70.26 | -2.07 | ✗ |
| MonoT5-base | TREC-COVID | 72.24 | 74.08 | 1.84 | ✗ | 72.13 | -0.11 | ✓ |
| MonoT5-base | NFCorpus | 34.81 | 35.06 | 0.25 | ✓ | 34.97 | 0.16 | ✓ |
| MonoT5-base | SciFact | 73.14 | 73.24 | 0.1 | ✓ | 72.87 | -0.27 | ✓ |

nDCG@10 × 100; ngưỡng đạt: BM25 ±0,5, reranker ±1,0. Bài báo: Abdallah et al. 2025, How Good are LLM-based Rerankers? (EMNLP Findings), arXiv:2508.16757. Rankify (toolkit của bài báo) chỉ đưa `context.text` vào reranker; RankGPT gốc đưa 'Title: … Content: …'. BM25 NFCorpus của Pyserini 2CR là 32,2 (≠ 30,75 trong bài) — xem mục 10.3 của plan.
