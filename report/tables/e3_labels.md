### SciFact-Open — giao 190 claim có bằng chứng ở cả hai bộ nhãn
| Hệ thống | nDCG@10 nhãn gốc | nDCG@10 nhãn đã soát | Δ | R@10 gốc | R@10 soát | Hạng gốc → soát |
|---|---:|---:|---:|---:|---:|:---:|
| R1 LambdaMART | 67.04 | 69.14 | 2.11 | 80.71 | 78.69 | 1 → 1 |
| R0 BM25 (Pyserini flat) | 60.68 | 62.12 | 1.44 | 71.32 | 69.36 | 2 → 2 |

Kendall τ = 1.000, 0 cặp hệ thống đổi thứ tự / 2 hệ thống

Không báo Judged@10: repo SciFact-Open không phát hành các cặp đã chấm là không liên quan.

### SciFact-Open — toàn bộ claim hợp lệ của từng bộ nhãn
| Hệ thống | nDCG@10 nhãn gốc | nDCG@10 nhãn đã soát | Δ | R@10 gốc | R@10 soát | Hạng gốc → soát |
|---|---:|---:|---:|---:|---:|:---:|
| R1 LambdaMART | 67.04 | 67.29 | 0.25 | 80.71 | 77.37 | 1 → 1 |
| R0 BM25 (Pyserini flat) | 60.68 | 60.79 | 0.12 | 71.32 | 68.21 | 2 → 2 |

Kendall τ = 1.000, 0 cặp hệ thống đổi thứ tự / 2 hệ thống

Không báo Judged@10: repo SciFact-Open không phát hành các cặp đã chấm là không liên quan.

### TREC-COVID — nhãn theo vòng so với nhãn đầy đủ (30 topic)
| Nhãn tới hết vòng | Số cặp có nhãn | τ (nDCG@10) | τ (condensed) | Cặp đổi thứ tự |
|---|---:|---:|---:|---:|
| 1.0 | 7569 | -1.000 | 1.000 | 1 |
| 2.0 | 16727 | 1.000 | 1.000 | 0 |
| 3.0 | 24775 | 1.000 | 1.000 | 0 |
| 4.0 | 30860 | 1.000 | 1.000 | 0 |
