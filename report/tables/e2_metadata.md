| Hệ thống | Q-q | Q-kw | Q-qn | Q-q+M1 | Q-kw+M1 | Q-qn+M1 |
|---|---:|---:|---:|---:|---:|---:|
| R0 BM25 (first-stage, truy vấn đổi) | 59.47 | 62.13 | 66.74 | — | — | — |
| R2 BiLSTM-ESIM | 55.38 | 51.07 | 63.25 | 55.04 | 51.90 | 63.52 |
| R2b BiLSTM-ESIM v2 (à la carte + khớp từ) | 56.54 | 52.72 | 64.18 | 57.05 | 54.03 | 64.63 |
| R3 MedCPT Cross-Encoder | 68.79 | 75.43 | 68.52 | 72.08 | 75.30 | 68.81 |
| R4 bge-reranker-v2-m3 | 78.57 | 78.17 | 79.04 | 78.52 | 78.00 | 78.84 |
| R5s GPT-6 Luna listwise | — | — | — | — | — | — |
| R6 Jev listwise | — | — | — | — | — | — |
| R1 LambdaMART (CV 5-fold trên TREC-COVID) | 69.03 | — | — | 70.84 | — | — |

TREC-COVID, nDCG@10 × 100. Q-kw = trường `query` (từ khóa), Q-q = `question` (mặc định BEIR), Q-qn = question + narrative; +M1 = chèn dòng metadata (journal, năm, loại bài, MeSH) trước abstract. Ứng viên giữ cố định (BM25 Q-q top-100), chỉ đổi thứ đưa vào reranker; riêng dòng R0 là BM25 chạy lại với truy vấn đổi.

### Tiêu chí 2×2 (Jev, GPT)
| Hệ thống | Bộ | Tiêu chí chung | Tiêu chí y khoa / narrative | Δ | p |
|---|---|---:|---:|---:|---:|
| R6 | TREC-COVID | — | — | — | — |
| R6 | NFCorpus | — | — | — | — |
| R6 | SciFact | — | — | — | — |
| R5s | TREC-COVID | — | — | — | — |
| R5s | NFCorpus | — | — | — | — |
| R5s | SciFact | — | — | — | — |

### Jev listwise và pointwise
| Bộ | Jev listwise | Jev pointwise |
|---|---:|---:|
| TREC-COVID | — | — |
| NFCorpus | — | — |
| SciFact | — | — |

### Thiên vị vị trí (xáo thứ tự ứng viên 3 lần)
| Hệ thống | Bộ | τ TB (xáo so với gốc) | nDCG@10 gốc | Biên độ nDCG@10 qua 4 lần |
|---|---|---:|---:|---:|
| gpt_small | TREC-COVID | — | — | — |
| gpt_small | NFCorpus | — | — | — |
| jev | TREC-COVID | — | — | — |
| jev | NFCorpus | — | — | — |

### Boost hậu kỳ theo độ trùng MeSH (TREC-COVID, λ chọn bằng CV 5-fold)
| Hệ thống | Gốc | + λ·MeSH (CV) | Δ | p | λ theo fold |
|---|---:|---:|---:|---:|---|
| R0 BM25 (Pyserini flat) | 59.47 | 58.92 | -0.55 | 0.197 | 2.0, 1.0, 0.25, 0.5, 1.0 |
| R1 LambdaMART | 68.93 | 68.39 | -0.54 | 0.210 | 1.0, 0.1, 0.1, 0.1, 0.1 |
| R2 BiLSTM-ESIM | 59.47 | 59.47 | -0.00 | 1.000 | 0.0, 0.0, 0.0, 0.0, 0.0 |
| R2b BiLSTM-ESIM v2 (à la carte + khớp từ) | 56.22 | 56.06 | -0.16 | 0.252 | 0.0, 0.1, 0.0, 0.0, 0.0 |
| R3 MedCPT Cross-Encoder | 68.79 | 67.85 | -0.94 | 0.133 | 0.0, 0.25, 0.0, 0.25, 0.0 |
| R4 bge-reranker-v2-m3 | 78.57 | 78.53 | -0.04 | 0.609 | 0.0, 0.0, 0.1, 0.0, 0.0 |
| R7 Qwen3-Reranker-4B | 85.00 | 84.97 | -0.03 | 0.829 | 0.1, 0.25, 0.1, 0.1, 0.1 |
| X1 bge-reranker-base | 68.61 | 68.30 | -0.30 | 0.431 | 0.5, 1.0, 0.25, 0.5, 0.5 |
| X2 bge-reranker-large | 74.23 | 74.09 | -0.14 | 0.630 | 0.25, 0.0, 0.0, 0.0, 0.0 |
| X3 mxbai-rerank-base | 83.06 | 82.42 | -0.64 | 0.071 | 1.0, 0.0, 1.0, 0.0, 0.0 |
| X4 MonoT5-base | 74.08 | 74.08 | -0.00 | 1.000 | 0.0, 0.0, 0.0, 0.0, 0.0 |
