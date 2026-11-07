| Hệ thống | Loại | p50 (ms/truy vấn) | p95 | p99 | USD / 1.000 truy vấn | nDCG@10 TB 3 bộ |
|---|---|---:|---:|---:|---:|---:|
| R0 BM25 (Pyserini flat) | local-cpu | — | — | — | 0.0000 | 53.18 |
| R2 BiLSTM-ESIM | local-gpu | 57 | 64 | 68 | 0.0056 | 51.38 |
| R2b BiLSTM-ESIM v2 (à la carte + khớp từ) | local-gpu | 58 | 63 | 68 | 0.0057 | 51.14 |
| R3 MedCPT Cross-Encoder | local-gpu | 643 | 765 | 807 | 0.0634 | 61.02 |
| X1 bge-reranker-base | local-gpu | 734 | 799 | 816 | 0.0711 | 57.24 |
| X3 mxbai-rerank-base | local-gpu | 1742 | 2044 | 2205 | 0.1703 | 63.52 |
| X2 bge-reranker-large | local-gpu | 2247 | 2427 | 2467 | 0.2172 | 60.75 |
| R4 bge-reranker-v2-m3 | local-gpu | 2275 | 2459 | 2491 | 0.2201 | 62.08 |
| X4 MonoT5-base | local-gpu | 4318 | 4641 | 4696 | 0.4181 | 60.79 |
| R7 Qwen3-Reranker-4B | local-gpu | 25042 | 31521 | 34035 | 2.4843 | 67.24 |

Local: Tesla T4 trên Kaggle, mỗi truy vấn 100 ứng viên, quy USD theo giá thuê T4 trong configs/pricing.yaml (ước lượng). API: tổng chi phí thật từ log / số truy vấn; độ trễ là tổng các lệnh gọi tuần tự của một truy vấn.
