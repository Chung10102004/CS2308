### BiLSTM-ESIM: v1 → v2 và ablation
| Phiên bản | Số seed | dev nDCG@10 (TB điểm tốt nhất) | TREC-COVID | NFCorpus | SciFact |
|---|---:|---:|---:|---:|---:|
| v1: BioWordVec cố định, OOV ngẫu nhiên, ≤8 epoch | 3 | 0.4932 | 55.38 ± 3.10 | 26.44 ± 1.52 | 72.30 ± 0.45 |
| v2: + vector OOV à la carte (học tiếp) + kênh khớp từ, ≤15 epoch ← chọn (R2b) | 3 | 0.4898 | 56.54 ± 0.37 | 26.73 ± 1.61 | 70.15 ± 1.44 |
| v2 chỉ vector à la carte (không kênh khớp từ) | 1 | 0.5012 | 60.44 | 27.29 | 72.53 |
| v2 chỉ kênh khớp từ (OOV ngẫu nhiên, học tiếp) | 1 | 0.5073 | 53.88 | 28.66 | 73.75 |

BM25 trên cùng dev: 0,4979 (NFCorpus 0,2886; SciFact 0,7071). R2b = biến thể v2 có dev TB cao nhất trong các bản đủ 3 seed; test chỉ để báo cáo. Lưu ý: dev (NFCorpus, SciFact) không chứa từ vựng COVID, nên không phản ánh được lợi ích của vector à la carte trên TREC-COVID.

### RRF ensemble — forward selection trên dev (k = 60)
| Bước | Thành viên | dev nDCG@10 | Ứng viên tốt nhất để thêm (dev) |
|---:|---|---:|---|
| 1 | qwen3_4b | 0.5745 | +medcpt_ce 0.5711, +mxbai_base 0.5655, +bge_large 0.5599 |

Không tổ hợp nào hơn qwen3_4b đơn lẻ trên dev (ngưỡng +0,001) → không có dòng ensemble riêng trong bảng chính.

Điểm dev từng hệ thống: qwen3_4b 0.5745, medcpt_ce 0.5454, mxbai_base 0.5387, monot5_base 0.5367, bge_large 0.5304, bge_v2_m3 0.5282, bge_base 0.5180, bm25 0.4979. Ứng viên chỉ gồm hệ thống zero-shot.
