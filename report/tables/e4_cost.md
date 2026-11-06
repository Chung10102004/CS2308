| Hệ thống | Loại | p50 (ms/truy vấn) | p95 | p99 | USD / 1.000 truy vấn | nDCG@10 TB 3 bộ |
|---|---|---:|---:|---:|---:|---:|
| R0 BM25 (Pyserini flat) | local-cpu | — | — | — | 0.0000 | 53.18 |
| R3 MedCPT Cross-Encoder | local-gpu | 533 | 610 | 2378 | 0.0587 | — |

Local: Tesla T4 trên Kaggle, mỗi truy vấn 100 ứng viên, quy USD theo giá thuê T4 trong configs/pricing.yaml (ước lượng). API: tổng chi phí thật từ log / số truy vấn; độ trễ là tổng các lệnh gọi tuần tự của một truy vấn.
