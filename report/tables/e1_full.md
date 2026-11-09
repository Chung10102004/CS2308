| Hệ thống | Bộ | nDCG@10 | KTC 95% | MRR@10 | R@10 | R@100 | Judged@10 |
|---|---|---:|---|---:|---:|---:|---:|
| R0 BM25 (Pyserini flat) | TREC-COVID | 59.47 | 52.41–66.65 | 85.29 | 1.58 | 10.91 | 91.2 |
| R0 BM25 (Pyserini flat) | NFCorpus | 32.18 | 28.75–35.71 | 52.38 | 15.41 | 24.57 | 29.7 |
| R0 BM25 (Pyserini flat) | SciFact | 67.89 | 63.47–72.31 | 64.57 | 80.38 | 92.53 | 8.8 |
| R1 LambdaMART | TREC-COVID | 71.37 | 65.09–77.32 | 92.17 | 1.90 | 10.91 | 95.6 |
| R1 LambdaMART | NFCorpus | 35.67 | 32.20–39.34 | 57.44 | 16.35 | 24.57 | 32.3 |
| R1 LambdaMART | SciFact | 75.97 | 72.27–79.68 | 72.40 | 89.99 | 92.53 | 10.0 |
| R2 BiLSTM-ESIM | TREC-COVID | 55.38 | 48.09–62.74 | 75.61 | 1.55 | 10.91 | 86.2 |
| R2 BiLSTM-ESIM | NFCorpus | 26.44 | 23.38–29.55 | 41.47 | 13.68 | 24.57 | 27.0 |
| R2 BiLSTM-ESIM | SciFact | 72.30 | 68.42–76.08 | 68.15 | 86.80 | 92.53 | 9.8 |
| R2b BiLSTM-ESIM v2 (à la carte + khớp từ) | TREC-COVID | 56.54 | 48.97–64.10 | 77.30 | 1.59 | 10.91 | 90.0 |
| R2b BiLSTM-ESIM v2 (à la carte + khớp từ) | NFCorpus | 26.73 | 23.68–29.87 | 42.21 | 13.65 | 24.57 | 27.1 |
| R2b BiLSTM-ESIM v2 (à la carte + khớp từ) | SciFact | 70.15 | 66.21–74.02 | 66.15 | 84.52 | 92.53 | 9.5 |
| R3 MedCPT Cross-Encoder | TREC-COVID | 68.79 | 61.61–75.82 | 89.84 | 1.92 | 10.91 | 92.2 |
| R3 MedCPT Cross-Encoder | NFCorpus | 34.68 | 31.31–38.27 | 56.23 | 16.50 | 24.57 | 31.5 |
| R3 MedCPT Cross-Encoder | SciFact | 79.58 | 75.76–83.22 | 76.84 | 90.12 | 92.53 | 10.1 |
| R4 bge-reranker-v2-m3 | TREC-COVID | 78.57 | 72.69–84.30 | 92.22 | 2.13 | 10.91 | 98.2 |
| R4 bge-reranker-v2-m3 | NFCorpus | 33.69 | 30.38–37.16 | 54.81 | 15.97 | 24.57 | 30.6 |
| R4 bge-reranker-v2-m3 | SciFact | 73.99 | 69.64–78.23 | 71.36 | 84.16 | 92.53 | 9.4 |
| R5s GPT-6 Luna listwise | TREC-COVID | 85.45 | 80.96–89.63 | 96.67 | 2.35 | 10.91 | 97.0 |
| R5s GPT-6 Luna listwise | NFCorpus | 38.60 | 35.11–42.24 | 60.76 | 17.65 | 24.57 | 34.3 |
| R5s GPT-6 Luna listwise | SciFact | 79.77 | 75.87–83.57 | 77.55 | 88.57 | 92.53 | 10.0 |
| R7 Qwen3-Reranker-4B | TREC-COVID | 85.00 | 79.51–90.04 | 97.40 | 2.29 | 10.91 | 98.8 |
| R7 Qwen3-Reranker-4B | NFCorpus | 37.37 | 33.89–40.90 | 59.91 | 17.28 | 24.57 | 33.4 |
| R7 Qwen3-Reranker-4B | SciFact | 79.35 | 75.53–83.05 | 76.24 | 90.76 | 92.53 | 10.2 |
| X1 bge-reranker-base | TREC-COVID | 68.61 | 61.25–75.69 | 83.83 | 1.84 | 10.91 | 93.8 |
| X1 bge-reranker-base | NFCorpus | 31.55 | 28.24–34.98 | 54.15 | 14.56 | 24.57 | 29.0 |
| X1 bge-reranker-base | SciFact | 71.55 | 67.25–75.75 | 68.55 | 83.36 | 92.53 | 9.3 |
| X2 bge-reranker-large | TREC-COVID | 74.23 | 67.74–80.55 | 90.83 | 1.95 | 10.91 | 95.6 |
| X2 bge-reranker-large | NFCorpus | 33.83 | 30.52–37.30 | 55.45 | 15.79 | 24.57 | 30.8 |
| X2 bge-reranker-large | SciFact | 74.20 | 69.90–78.35 | 71.43 | 84.69 | 92.53 | 9.6 |
| X3 mxbai-rerank-base | TREC-COVID | 83.06 | 77.16–88.35 | 96.50 | 2.25 | 10.91 | 97.8 |
| X3 mxbai-rerank-base | NFCorpus | 35.48 | 32.04–38.97 | 58.82 | 16.77 | 24.57 | 31.8 |
| X3 mxbai-rerank-base | SciFact | 72.03 | 67.48–76.30 | 69.27 | 82.77 | 92.53 | 9.3 |
| X4 MonoT5-base | TREC-COVID | 74.08 | 67.29–80.65 | 92.23 | 1.96 | 10.91 | 97.6 |
| X4 MonoT5-base | NFCorpus | 35.06 | 31.65–38.58 | 57.59 | 16.50 | 24.57 | 31.3 |
| X4 MonoT5-base | SciFact | 73.24 | 68.96–77.40 | 70.79 | 83.86 | 92.53 | 9.5 |
