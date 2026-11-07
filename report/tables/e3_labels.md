### SciFact-Open — giao 190 claim có bằng chứng ở cả hai bộ nhãn
| Hệ thống | nDCG@10 nhãn gốc | nDCG@10 nhãn đã soát | Δ | R@10 gốc | R@10 soát | Hạng gốc → soát |
|---|---:|---:|---:|---:|---:|:---:|
| R7 Qwen3-Reranker-4B | 70.47 | 74.61 | 4.14 | 82.60 | 82.67 | 2 → 1 |
| R3 MedCPT Cross-Encoder | 70.82 | 74.32 | 3.50 | 83.68 | 83.14 | 1 → 2 |
| R4 bge-reranker-v2-m3 | 67.89 | 72.50 | 4.62 | 79.53 | 80.36 | 3 → 3 |
| X3 mxbai-rerank-base | 65.07 | 70.86 | 5.79 | 78.42 | 80.42 | 5 → 4 |
| X2 bge-reranker-large | 64.06 | 70.82 | 6.76 | 77.21 | 79.30 | 7 → 5 |
| R1 LambdaMART | 67.04 | 69.14 | 2.11 | 80.71 | 78.69 | 4 → 6 |
| X4 MonoT5-base | 64.25 | 68.03 | 3.78 | 75.82 | 76.41 | 6 → 7 |
| X1 bge-reranker-base | 60.50 | 65.96 | 5.47 | 72.12 | 73.91 | 10 → 8 |
| R2 BiLSTM-ESIM | 60.73 | 62.79 | 2.07 | 76.91 | 74.54 | 8 → 9 |
| R0 BM25 (Pyserini flat) | 60.68 | 62.12 | 1.44 | 71.32 | 69.36 | 9 → 10 |
| R2b BiLSTM-ESIM v2 (à la carte + khớp từ) | 55.98 | 57.65 | 1.67 | 70.92 | 67.98 | 11 → 11 |

Kendall τ = 0.782, 6 cặp hệ thống đổi thứ tự / 11 hệ thống

Không báo Judged@10: repo SciFact-Open không phát hành các cặp đã chấm là không liên quan.

### SciFact-Open — toàn bộ claim hợp lệ của từng bộ nhãn
| Hệ thống | nDCG@10 nhãn gốc | nDCG@10 nhãn đã soát | Δ | R@10 gốc | R@10 soát | Hạng gốc → soát |
|---|---:|---:|---:|---:|---:|:---:|
| R7 Qwen3-Reranker-4B | 70.47 | 73.67 | 3.20 | 82.60 | 81.96 | 2 → 1 |
| R3 MedCPT Cross-Encoder | 70.82 | 72.92 | 2.10 | 83.68 | 81.98 | 1 → 2 |
| R4 bge-reranker-v2-m3 | 67.89 | 70.99 | 3.11 | 79.53 | 79.34 | 3 → 3 |
| X3 mxbai-rerank-base | 65.07 | 70.65 | 5.58 | 78.42 | 80.39 | 5 → 4 |
| X2 bge-reranker-large | 64.06 | 69.36 | 5.30 | 77.21 | 78.61 | 7 → 5 |
| R1 LambdaMART | 67.04 | 67.29 | 0.25 | 80.71 | 77.37 | 4 → 6 |
| X4 MonoT5-base | 64.25 | 66.68 | 2.43 | 75.82 | 75.88 | 6 → 7 |
| X1 bge-reranker-base | 60.50 | 65.22 | 4.73 | 72.12 | 73.55 | 10 → 8 |
| R2 BiLSTM-ESIM | 60.73 | 61.51 | 0.78 | 76.91 | 73.17 | 8 → 9 |
| R0 BM25 (Pyserini flat) | 60.68 | 60.79 | 0.12 | 71.32 | 68.21 | 9 → 10 |
| R2b BiLSTM-ESIM v2 (à la carte + khớp từ) | 55.98 | 55.84 | -0.14 | 70.92 | 66.16 | 11 → 11 |

Kendall τ = 0.782, 6 cặp hệ thống đổi thứ tự / 11 hệ thống

Không báo Judged@10: repo SciFact-Open không phát hành các cặp đã chấm là không liên quan.

### TREC-COVID — nhãn theo vòng so với nhãn đầy đủ (30 topic)
| Nhãn tới hết vòng | Số cặp có nhãn | τ (nDCG@10) | τ (condensed) | Cặp đổi thứ tự |
|---|---:|---:|---:|---:|
| 1.0 | 7569 | 0.418 | 0.745 | 16 |
| 2.0 | 16727 | 0.382 | 0.745 | 17 |
| 3.0 | 24775 | 0.636 | 0.818 | 10 |
| 4.0 | 30860 | 0.927 | 0.927 | 2 |
