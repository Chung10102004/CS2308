### SciFact-Open — giao 190 claim có bằng chứng ở cả hai bộ nhãn
| Hệ thống | nDCG@10 nhãn gốc | nDCG@10 nhãn đã soát | Δ | R@10 gốc | R@10 soát | Hạng gốc → soát |
|---|---:|---:|---:|---:|---:|:---:|
| R3 MedCPT Cross-Encoder | 70.82 | 74.32 | 3.50 | 83.68 | 83.14 | 1 → 1 |
| R4 bge-reranker-v2-m3 | 67.89 | 72.50 | 4.62 | 79.53 | 80.36 | 2 → 2 |
| X3 mxbai-rerank-base | 65.07 | 70.86 | 5.79 | 78.42 | 80.42 | 4 → 3 |
| X2 bge-reranker-large | 64.06 | 70.82 | 6.76 | 77.21 | 79.30 | 6 → 4 |
| R1 LambdaMART | 67.04 | 69.14 | 2.11 | 80.71 | 78.69 | 3 → 5 |
| X4 MonoT5-base | 64.25 | 68.03 | 3.78 | 75.82 | 76.41 | 5 → 6 |
| X1 bge-reranker-base | 60.50 | 65.96 | 5.47 | 72.12 | 73.91 | 9 → 7 |
| R2 BiLSTM-ESIM | 60.73 | 62.79 | 2.07 | 76.91 | 74.54 | 7 → 8 |
| R0 BM25 (Pyserini flat) | 60.68 | 62.12 | 1.44 | 71.32 | 69.36 | 8 → 9 |

Kendall τ = 0.722, 5 cặp hệ thống đổi thứ tự / 9 hệ thống

Không báo Judged@10: repo SciFact-Open không phát hành các cặp đã chấm là không liên quan.

### SciFact-Open — toàn bộ claim hợp lệ của từng bộ nhãn
| Hệ thống | nDCG@10 nhãn gốc | nDCG@10 nhãn đã soát | Δ | R@10 gốc | R@10 soát | Hạng gốc → soát |
|---|---:|---:|---:|---:|---:|:---:|
| R3 MedCPT Cross-Encoder | 70.82 | 72.92 | 2.10 | 83.68 | 81.98 | 1 → 1 |
| R4 bge-reranker-v2-m3 | 67.89 | 70.99 | 3.11 | 79.53 | 79.34 | 2 → 2 |
| X3 mxbai-rerank-base | 65.07 | 70.65 | 5.58 | 78.42 | 80.39 | 4 → 3 |
| X2 bge-reranker-large | 64.06 | 69.36 | 5.30 | 77.21 | 78.61 | 6 → 4 |
| R1 LambdaMART | 67.04 | 67.29 | 0.25 | 80.71 | 77.37 | 3 → 5 |
| X4 MonoT5-base | 64.25 | 66.68 | 2.43 | 75.82 | 75.88 | 5 → 6 |
| X1 bge-reranker-base | 60.50 | 65.22 | 4.73 | 72.12 | 73.55 | 9 → 7 |
| R2 BiLSTM-ESIM | 60.73 | 61.51 | 0.78 | 76.91 | 73.17 | 7 → 8 |
| R0 BM25 (Pyserini flat) | 60.68 | 60.79 | 0.12 | 71.32 | 68.21 | 8 → 9 |

Kendall τ = 0.722, 5 cặp hệ thống đổi thứ tự / 9 hệ thống

Không báo Judged@10: repo SciFact-Open không phát hành các cặp đã chấm là không liên quan.

### TREC-COVID — nhãn theo vòng so với nhãn đầy đủ (30 topic)
| Nhãn tới hết vòng | Số cặp có nhãn | τ (nDCG@10) | τ (condensed) | Cặp đổi thứ tự |
|---|---:|---:|---:|---:|
| 1.0 | 7569 | 0.278 | 0.667 | 13 |
| 2.0 | 16727 | 0.278 | 0.667 | 13 |
| 3.0 | 24775 | 0.556 | 0.778 | 8 |
| 4.0 | 30860 | 0.944 | 0.889 | 1 |
