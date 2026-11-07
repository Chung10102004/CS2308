### BiLSTM-ESIM: v1 → v2 và ablation
| Phiên bản | dev nDCG@10 (tốt nhất) | TREC-COVID | NFCorpus | SciFact |
|---|---:|---:|---:|---:|
| v1: BioWordVec cố định, OOV ngẫu nhiên, ≤8 epoch | 0.4932 | 55.38 ± 3.10 | 26.44 ± 1.52 | 72.30 ± 0.45 |
| v2: + vector OOV à la carte (học tiếp) + kênh khớp từ, ≤15 epoch | — | — | — | — |
| v2 bỏ kênh khớp từ (seed 0) | — | — | — | — |
| v2 bỏ vector à la carte (OOV ngẫu nhiên, học tiếp; seed 0) | — | — | — | — |

BM25 trên cùng dev: 0,4979 (NFCorpus 0,2886; SciFact 0,7071). Chọn phiên bản theo dev; test chỉ để báo cáo.
