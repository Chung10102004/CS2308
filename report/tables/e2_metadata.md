| Hệ thống | Q-q | Q-kw | Q-qn | Q-q+M1 | Q-kw+M1 | Q-qn+M1 |
|---|---:|---:|---:|---:|---:|---:|
| R0 BM25 (first-stage, truy vấn đổi) | 59.47 | 62.13 | 66.74 | — | — | — |
| R2 BiLSTM-ESIM | — | — | — | — | — | — |
| R3 MedCPT Cross-Encoder | — | — | — | — | — | — |
| R4 bge-reranker-v2-m3 | — | — | — | — | — | — |
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
