# So sánh các thế hệ reranker cho truy xuất y sinh trên benchmark có nhãn sẵn

> **Bản thảo có hỗ trợ của công cụ AI — nhóm cần đọc, rà soát và chịu trách nhiệm nội dung trước khi nộp.**
> Mọi con số lấy từ `results/` (sinh bằng `make report`) hoặc từ bảng của bài báo được trích (`src/eval/published.py`).
> Phạm vi cập nhật ngày 09/11/2026: chỉ dùng GPT-6 Luna cho API; không chạy thêm API sau E1. Các phân tích bổ sung tận dụng kết quả đã lưu.

## Tóm tắt

Đồ án đánh giá các mô hình xếp hạng lại tài liệu y sinh trên TREC-COVID, NFCorpus và SciFact, giữ nguyên danh sách ứng viên BM25 top-100 để so sánh công bằng. Các hệ thống gồm LambdaMART, BiLSTM-ESIM, cross-encoder chuyên y sinh và tổng quát, Qwen3-Reranker-4B và GPT-6 Luna. Toàn bộ đánh giá dùng nhãn chuẩn có sẵn, không dùng LLM làm người chấm. Trên 673 truy vấn, GPT-6 Luna đạt nDCG@10 × 100 lần lượt 85,45 / 38,60 / 79,77, hơn BM25 và bge-reranker-v2-m3 có ý nghĩa sau hiệu chỉnh Holm; trung bình ba bộ là 67,94. BiLSTM giúp trên SciFact nhưng không vượt BM25 trên hai bộ còn lại, cho thấy lợi ích của reranking phụ thuộc dữ liệu và cách biểu diễn. Phân tích SciFact-Open với 11 hệ thống cho thấy nhãn bổ sung làm đảo thứ tự 6 cặp hệ thống; phân tích TREC-COVID theo vòng được mở rộng thêm GPT bằng kết quả E1 đã lưu. Chi phí token ghi nhận của GPT là 3,7784 USD. Demo offline minh họa thứ hạng trước/sau mà không phát sinh lượt gọi API. Các thử nghiệm GPT với metadata, xáo thứ tự, SciFact-Open và cascade được ghi rõ là chưa chạy.

## 1. Giới thiệu

Mô hình ngôn ngữ lớn có thể trả lời câu hỏi y sinh trôi chảy nhưng vẫn bịa thông tin. Hướng phổ biến để giảm việc này là RAG (retrieval-augmented generation): truy xuất tài liệu liên quan rồi buộc mô hình trả lời dựa trên đó. Trong một hệ thống RAG, **reranker** là khâu quyết định những tài liệu nào thực sự được đưa vào ngữ cảnh. First-stage (ví dụ BM25) lấy về hàng trăm ứng viên, và reranker chọn ra vài tài liệu đầu.

Có nhiều thế hệ reranker: learning-to-rank trên đặc trưng thủ công, mạng LSTM đối sánh câu, cross-encoder dựa trên Transformer, LLM xếp hạng kiểu listwise, và gần đây là các mô hình quyết định chuyên dụng như Jev. Kết quả công bố cho từng thế hệ thường dùng ứng viên, kho và cách chấm khác nhau, nên khó so sánh trực tiếp. Ngoài ra, nhãn của các bộ đánh giá thường được gom theo pooling nên bị thiếu. Một reranker tìm ra bài liên quan nhưng chưa ai chấm sẽ bị tính là sai.

Đồ án trả lời bốn câu hỏi:

- **RQ1:** Trên cùng danh sách BM25 top-100, các reranker của nhóm (LambdaMART, BiLSTM-ESIM, MedCPT cross-encoder, Qwen3 và GPT-6 Luna) đứng ở đâu so với các dòng công bố được chọn từ Abdallah et al. (2025)?
- **RQ2:** Câu hỏi đầy đủ, mô tả nhu cầu (narrative) và metadata tài liệu (MeSH, loại bài, năm) giúp reranker nào?
- **RQ3:** Chấm bằng nhãn thiếu thì kết luận so sánh có đổi không?
- **RQ4:** Chi phí và độ trễ của mỗi lựa chọn là bao nhiêu?

**Đóng góp.** Đồ án có ba điểm khác với cách làm thông thường:

1. Toàn bộ đánh giá dùng nhãn có sẵn: không chấm tay, không dùng LLM làm người chấm.
2. Kết quả đặt trực tiếp vào bảng của Abdallah et al. (2025), sau khi đã tái lập được mốc BM25.
3. Ảnh hưởng của nhãn thiếu được đo bằng nhãn do chuyên gia soát lại (SciFact-Open) và nhãn theo từng vòng của NIST (TREC-COVID), thay vì bằng giả định.

## 2. Công trình liên quan

**Benchmark truy xuất zero-shot.**

- BEIR (Thakur et al., 2021) gom 18 bộ dữ liệu, trong đó có ba bộ y sinh dùng ở đây: TREC-COVID, NFCorpus và SciFact. Bài cho thấy BM25 là baseline khó vượt khi chuyển miền.
- BEIR cũng phân tích "lỗ" trong nhãn của TREC-COVID. Tỷ lệ bài trong top-10 chưa được chấm (Hole@10) dao động từ 1,6% (BM25 + cross-encoder) đến 31,8% (TAS-B). Sau khi chấm bổ sung 980 cặp, nDCG@10 của ANCE tăng từ 0,654 lên 0,735.

**LLM làm reranker.**

- RankGPT (Sun et al., 2023) cho GPT xếp hạng theo kiểu hoán vị, dùng cửa sổ trượt 20 đoạn với bước 10 trên BM25 top-100 lấy từ Pyserini.
- Các hướng sau đó gồm RankZephyr, ListT5, Setwise (Zhuang et al., 2024) và TourRank.
- Abdallah et al. (2025) gom 22 phương pháp với 40 biến thể vào cùng một thiết lập BM25 top-100. Đây là bảng mốc của đồ án.

**Reranker y sinh.** MedCPT (Jin et al., 2023) huấn luyện bi-encoder và cross-encoder bằng log tìm kiếm PubMed, rồi đánh giá zero-shot trên các bộ y sinh của BEIR.

**LSTM cho đối sánh văn bản.** ESIM (Chen et al., 2017) dùng BiLSTM mã hóa hai phía, căn chỉnh mềm, rồi BiLSTM tổng hợp. Đồ án dùng ESIM làm reranker, với embedding BioWordVec (Zhang et al., 2019).

**Nhãn thiếu.**

- TREC-COVID (Voorhees et al., 2020) xây nhãn qua 5 vòng pooling, tổng cộng 69.318 nhãn.
- SciFact-Open (Wadden et al., 2022) mở rộng SciFact lên 500K abstract. Nhóm tác giả gom dự đoán của 4 hệ thống và cho chuyên gia chấm, tìm thêm 251 cặp bằng chứng so với 209 cặp gốc.

## 3. Ngữ liệu

### 3.1 Các bộ dữ liệu

| Bộ | Truy vấn test | Kho | Bài đúng TB / truy vấn | Mức nhãn | Train / dev | Ai gán nhãn |
|---|---:|---:|---:|---|---|---|
| TREC-COVID | 50 | 171.332 | 493,5 | 0/1/2 | — | NIST (5 vòng pooling) |
| NFCorpus | 323 | 3.633 | 38,2 | 0/1/2 | 2.586 / 324 | Tự động từ link NutritionFacts.org |
| SciFact | 300 | 5.183 | 1,1 | nhị phân | 632 / 162 | Chuyên gia |
| SciFact-Open | 279 | 500.000 | 1,6 (nhãn đã soát) | nhị phân | — | Chuyên gia (gốc + pooling) |

Ghi chú về bảng:

- Số train/dev là số sau khi chia lại tập và loại câu gần trùng (`results/data_report/splits.json`).
- Đã xác minh rằng 300 claim test của BEIR SciFact trùng hoàn toàn với tập `claims_dev` gốc, và 279 claim của SciFact-Open đều thuộc tập test gốc. Vì vậy hai bộ không trùng claim với nhau.
- Loại 19 câu train gần trùng (TF-IDF cosine > 0,9) với một câu test bất kỳ. Ví dụ: "Obesity decreases life quality." xuất hiện ở cả train lẫn test.

### 3.2 Đặc điểm (`results/data_report/corpus_stats.json`, hình `fig_data_*`)

- **Độ dài truy vấn** (token trung bình):
  - TREC-COVID 10,6, dạng câu hỏi;
  - NFCorpus 3,3, chủ yếu là tiêu đề ngắn của bài viết phổ thông như "vitamin K";
  - SciFact 12,6, là một mệnh đề khoa học.
- **Truy vấn không có kết quả BM25:** 15 truy vấn NFCorpus, được tính 0 điểm như trec_eval `-c`.
- **Độ trùng từ** (tỷ lệ từ của truy vấn có trong bài, xét bài trong BM25 top-100):
  - TREC-COVID: bài đúng 0,61, bài sai 0,50;
  - NFCorpus: bài đúng 0,60, bài sai 0,35;
  - SciFact: bài đúng 0,50, bài sai 0,24.
  - TREC-COVID có khoảng cách nhỏ nhất. Đây là bộ mà tín hiệu từ vựng phân biệt kém nhất, nên kỳ vọng reranker ngữ nghĩa giúp nhiều nhất ở đây.
- **Recall@100 của BM25** (cận trên cho reranker): TREC-COVID 0,109, NFCorpus 0,246, SciFact 0,925. TREC-COVID thấp vì mỗi topic có khoảng 494 bài đúng, không phải vì BM25 kém.
- **Metadata TREC-COVID** (9.604 bài ứng viên): 47,8% có PMID, 40,1% có MeSH, 86,1% có tên tạp chí, 100% có năm.
- **Nhãn thiếu:**
  - TREC-COVID: nhãn tới hết vòng 1 trên 30 topic đầu có 7.569 cặp (2.038 liên quan), trong khi nhãn đầy đủ có 43.576 cặp (16.164 liên quan).
  - SciFact-Open: 81 trên 279 claim được thêm bằng chứng nhờ pooling.

## 4. Phương pháp

### 4.1 Thiết lập chung
- **Ứng viên:** BM25 của Pyserini với index BEIR "flat" dựng sẵn, lấy top-100. Mọi reranker xếp lại đúng danh sách này, giống RankGPT và Abdallah et al. (2025).
- **SciFact-Open:** nhóm tự dựng index Lucene cho kho 500K abstract, cùng cấu hình BM25.

### 4.2 Các reranker

| ID | Reranker | Cách dùng |
|---|---|---|
| R0 | BM25 | Không xếp lại |
| R1 | LambdaMART (LightGBM, lambdarank) | 11 đặc trưng: điểm và hạng BM25, TF-IDF cosine, MedCPT bi-encoder (thô và chuẩn hóa z), độ trùng từ với truy vấn và tiêu đề, độ dài, có tiêu đề hay không. Train trên NFCorpus + SciFact, early stopping trên dev, 3 seed |
| R2 | BiLSTM-ESIM | Mục 4.3 |
| R3 | MedCPT Cross-Encoder | Zero-shot |
| R4 | bge-reranker-v2-m3 | Zero-shot, dùng làm mốc tái lập |
| R5s | GPT-6 Luna (listwise, toàn bộ top-100) | Prompt hoán vị của RankGPT; cửa sổ 20, bước 10; đoạn văn cắt 300 từ; `reasoning_effort=none`; đầu ra JSON qua structured outputs |
| R7 | Qwen3-Reranker-4B | Mô hình mã nguồn mở, kết quả suy luận lưu từ Kaggle |

### 4.3 BiLSTM-ESIM (thành phần LSTM)

- **Embedding:** BioWordVec 200 chiều (trên PubMed + MIMIC-III), giữ cố định. Vocab của dữ liệu có 168.345 từ, BioWordVec phủ 94,7%. Từ còn thiếu khởi tạo ngẫu nhiên N(0; 0,1).
- **Mã hóa:** một BiLSTM, 200 chiều mỗi hướng, chạy riêng trên truy vấn (tối đa 64 token) và trên tiêu đề + abstract (tối đa 256 token).
- **Căn chỉnh mềm:** ma trận e = a·bᵀ. Mỗi token truy vấn được biểu diễn lại bằng trung bình có trọng số softmax của các token tài liệu, và ngược lại. Token đệm bị che.
- **Tăng cường và tổng hợp:** ghép [a; ã; a − ã; a ⊙ ã], chiếu xuống 200 chiều qua ReLU, rồi đưa qua BiLSTM tổng hợp.
- **Gộp và chấm điểm:** lấy trung bình và max theo chiều thời gian ở cả hai phía (1.600 chiều), rồi MLP (tanh, dropout 0,3) ra một điểm.
- **Huấn luyện:**
  - mỗi nhóm có 1 bài đúng và 7 bài sai, bài sai lấy ngẫu nhiên từ BM25 top-100 của chính truy vấn đó;
  - loss là softmax cross-entropy trên nhóm (listwise);
  - Adam, lr 4·10⁻⁴, clip gradient 10;
  - early stopping theo nDCG@10 trên dev (NFCorpus dev + 20% train SciFact), patience 2;
  - 3 seed.

### 4.4 Đánh giá
- **Metric chính:** nDCG@10 tính bằng `ir_measures`/pytrec_eval, nhãn nhiều mức giữ nguyên, truy vấn không có kết quả tính 0 (như `trec_eval -c`).
- **Metric phụ:** MRR@10, R@10, R@100, Judged@10.
- **Kiểm định:** paired bootstrap 10.000 lần trên điểm từng truy vấn, hiệu chỉnh Holm.
- **So thứ hạng hệ thống:** Kendall τ.
- **Nguyên tắc:** không có bước chấm tay và không có LLM làm người chấm.

## 5. Kết quả

### 5.1 Tái lập (E0) — `report/tables/e0_reproduction.md`

| Bộ | BM25 của nhóm | Bài báo |
|---|---:|---:|
| TREC-COVID | 59,47 | 59,47 |
| SciFact | 67,89 | 67,89 |
| NFCorpus | 32,18 | 30,75 |

- TREC-COVID và SciFact khớp tuyệt đối.
- NFCorpus ra 32,18, khớp trang tái lập của Pyserini (0,322) nhưng cao hơn số trong bài 1,43 điểm. Nhóm đã thử hai giả thuyết về cách tính truy vấn không có kết quả: tính bằng 0 ra 32,18, bỏ đi ra 33,75. Cả hai đều không ra 30,75.
- Vì vậy, trên NFCorpus nhóm so sánh chủ yếu bằng mức tăng so với BM25.
- **Reranker** (bảng `e0_reproduction.md`): với cấu hình của nhóm ("tiêu đề. abstract", fp16, cắt 512 token), **13/15** dòng của 5 model có trong bài báo khớp trong ±1 điểm. Hai dòng không khớp đều ở TREC-COVID: bge-reranker-v2-m3 (78,57 so với 74,79) và MonoT5-base (74,08 so với 72,24).
- **Tìm nguyên nhân.** Đọc mã nguồn cho thấy hai toolkit đưa văn bản vào reranker khác nhau:
  - Rankify (toolkit của bài báo) chỉ đưa abstract (`context.text`);
  - RankGPT gốc đưa "Title: … Content: …" (`rank_gpt.py`, dòng 113–114).
- **Kiểm chứng.** Nhóm chạy lại 5 model theo cách của Rankify (chỉ abstract, fp32, không cắt 512 token):
  - Hai dòng TREC-COVID trên khớp gần như tuyệt đối: 74,26 (−0,53) và 72,13 (−0,11).
  - Nhưng 8 dòng khác lại lệch tới 2–3 điểm.
- **Kết luận.** Chính bảng công bố trộn cách nhập văn bản giữa các dòng: các dòng chép từ RankGPT có tiêu đề, phần lớn dòng chạy bằng Rankify khớp với cấu hình có tiêu đề, và một số dòng TREC-COVID không có tiêu đề. Nhóm giữ một cấu hình thống nhất ("tiêu đề. abstract") cho mọi reranker của mình và chú thích rằng trên TREC-COVID, một số dòng công bố có thể thấp hơn tới khoảng 4 điểm chỉ vì thiếu tiêu đề.

### 5.2 Bảng chính (E1) — `report/tables/e1_main.md`, hình `fig_e1_ranking.png`

LambdaMART (R1) đạt các mức sau, đều hơn BM25 có ý nghĩa thống kê:

| Bộ | R1 LambdaMART | Xếp hạng tương đương trong bảng công bố |
|---|---:|---|
| TREC-COVID | 71,37 ± 2,59 | Giữa monoBERT (70,01) và MonoT5-base (72,24) |
| NFCorpus | 35,67 ± 0,07 | |
| SciFact | 75,97 ± 0,37 | Trên mọi reranker cỡ base trong bảng; dưới MonoT5-3B (76,57) |

Phần lớn sức mạnh của R1 đến từ đặc trưng MedCPT bi-encoder: hai đặc trưng `medcpt_z` và `medcpt` chiếm khoảng 68% tổng gain ở seed 0 (`results/e1/lambdamart_train.json`).

**BiLSTM-ESIM (R2), 3 seed:**

| Bộ | R2 | So với BM25 (p sau hiệu chỉnh Holm) |
|---|---:|---|
| SciFact | 72,30 ± 0,45 | +4,41 (p = 0,008) |
| TREC-COVID | 55,38 ± 3,10 | −4,09, không có ý nghĩa |
| NFCorpus | 26,44 ± 1,52 | −5,74 (p < 0,001) |

Trên dev, điểm tốt nhất của R2 (0,48–0,505) xấp xỉ BM25 (0,498): hơn ở SciFact dev (0,72–0,77 so với 0,707), kém ở NFCorpus dev (0,23–0,26 so với 0,289). Ba nguyên nhân, đã kiểm bằng số liệu (`results/data_report/bilstm_oov.json`):

1. **TREC-COVID — từ vựng mới.** BioWordVec được huấn luyện trước đại dịch. 78% truy vấn TREC-COVID chứa ít nhất một từ không có vector ("covid-19" xuất hiện 31 lần, "sars-cov-2" 7 lần), và vì embedding bị giữ cố định nên khái niệm trung tâm của mọi truy vấn chỉ là vector ngẫu nhiên. NFCorpus không có từ OOV nào; SciFact có 0,5% token OOV.
2. **NFCorpus — truy vấn rất ngắn, tín hiệu từ vựng mạnh.** Truy vấn trung bình 3,3 token bằng ngôn ngữ phổ thông, nên căn chỉnh mềm có rất ít để căn. Ở đây BM25 phân biệt tốt (độ trùng từ 0,60 với bài đúng so với 0,35 với bài sai), trong khi ESIM không có đặc trưng khớp chính xác.
3. **Chưa hội tụ hẳn.** Seed 0 vẫn tăng ở epoch cuối (epoch 7, giới hạn 8 epoch).

Dù vậy, R2 mang tín hiệu bổ sung cho BM25. Ghép hai danh sách bằng RRF (k = 60, không chỉnh tham số) cho 62,43 / 33,05 / 73,55 trên TREC-COVID / NFCorpus / SciFact, hơn BM25 ở cả ba bộ.

**Cross-encoder** (cấu hình của nhóm: "tiêu đề. abstract", cắt 512 token, fp16):

| Reranker | TREC-COVID | NFCorpus | SciFact |
|---|---:|---:|---:|
| MedCPT-CE (R3) | 68,79 | 34,68 | **79,58** |
| bge-reranker-v2-m3 (R4) | 78,57 | 33,69 | 73,99 |
| mxbai-rerank-base | 83,06 | 35,48 | 72,03 |
| bge-reranker-large | 74,23 | 33,83 | 74,20 |
| MonoT5-base | 74,08 | 35,06 | 73,24 |
| bge-reranker-base | 68,61 | 31,55 | 71,55 |

- **Model chuyên y sinh thắng ở bộ gần miền huấn luyện nhất.** MedCPT-CE đạt 79,58 trên SciFact, cao hơn mọi dòng của bảng công bố (cao nhất là InRanker-3B 78,31) và hơn bge-reranker-v2-m3 có ý nghĩa thống kê. Nhưng trên TREC-COVID, nó kém bge-reranker-v2-m3 gần 10 điểm.
- **Trung bình 3 bộ,** mxbai-rerank-base đứng đầu nhóm local (63,52), tiếp theo là bge-reranker-v2-m3 (62,08) và MedCPT-CE (61,02). LambdaMART (61,00) ngang MedCPT-CE dù chỉ là cây quyết định trên đặc trưng; phần lớn sức mạnh của nó đến từ chính đặc trưng MedCPT bi-encoder.

**Qwen3-Reranker-4B (R7, LLM mã nguồn mở 2025, zero-shot, instruction mặc định):**

| Bộ | Qwen3-4B | Nhận xét |
|---|---:|---|
| TREC-COVID | 85,00 | ngang RankGPT gpt-4 (85,51), hơn mọi dòng còn lại của bảng |
| NFCorpus | 37,37 | |
| SciFact | 79,35 | hơn mọi dòng công bố; xấp xỉ MedCPT-CE (79,58) |
| Trung bình | 67,24 | cao hơn RankGPT gpt-4 (66,31) |

Model này chạy trên 2 GPU T4 của Kaggle, không tốn tiền API. Lưu ý: dòng RankGPT gpt-4 chỉ xếp lại top-30 của gpt-3.5.

**RRF ensemble.** Forward selection trên dev (NFCorpus dev + SciFact dev), ứng viên chỉ gồm các reranker zero-shot:
- Khi chưa có Qwen3, tổ hợp được chọn là MedCPT-CE + mxbai + bge-large (dev 0,5606), cho test 82,25 / 36,32 / 77,36.
- Khi có Qwen3, dev của Qwen3 đơn lẻ là 0,5745, và thêm bất kỳ hệ thống nào đều làm dev giảm (tốt nhất là +MedCPT-CE, 0,5711).
- Vậy ensemble không giúp. Nhóm báo cáo đúng như vậy, không chọn tổ hợp bằng test.

Hai bản ablation của BiLSTM-ESIM v2 (bỏ kênh khớp từ hoặc bỏ vector OOV à la carte) hiện mới có một seed mỗi bản. Kết quả ở bảng `improvements.md` chỉ có tính thăm dò; không dùng chúng để kết luận thành phần nào tốt hơn một cách ổn định. Bản v1 và bản v2 đầy đủ có ba seed.

**GPT-6 Luna (R5s), chạy API ngày 09/11/2026.** Với `reasoning_effort=none`, cửa sổ 20 tài liệu, bước 10 trên cùng danh sách BM25 top-100, mô hình đạt nDCG@10 × 100 lần lượt **85,45 / 38,60 / 79,77** trên TREC-COVID / NFCorpus / SciFact; trung bình **67,94**. Mức tăng so với BM25 là **+25,98 / +6,43 / +11,88 điểm**. Mô hình hơn BM25 và bge-reranker-v2-m3 có ý nghĩa trên cả ba bộ (paired bootstrap 10.000 lần, hiệu chỉnh Holm, p < 0,05). Đợt chạy E1 gồm 673 truy vấn, trong đó 15 truy vấn NFCorpus không có ứng viên vẫn được tính 0 khi đánh giá; toàn bộ tài liệu ứng viên được giữ nguyên. Log ghi 5.182 lượt gọi, không có lỗi phản hồi/parse được ghi nhận. Chi tiết: `results/e1/luna_run_summary.json`.

Đợt API chỉ chạy GPT-6 Luna trong E1. GPT lớn và Jev đã được loại khỏi phạm vi thực hiện. Phân tích nhãn theo vòng TREC-COVID và chi phí được tính tiếp từ kết quả E1 mà không gọi API mới; các thử nghiệm GPT cần đầu vào mới chưa chạy.

### 5.3 Metadata và tiêu chí (E2) — `report/tables/e2_metadata.md`

- **BM25 khi đổi truy vấn** (TREC-COVID): từ khóa 62,13; câu hỏi 59,47; câu hỏi + narrative 66,74.
- **LambdaMART CV 5-fold trên TREC-COVID:** M0 69,03, M1 (thêm metadata) 70,84.
- **Dạng truy vấn đưa vào reranker** (ứng viên giữ cố định), nDCG@10 khi đổi câu hỏi → từ khóa → câu hỏi + narrative:

  | Reranker | Câu hỏi | Từ khóa | Câu hỏi + narrative |
  |---|---:|---:|---:|
  | MedCPT-CE | 68,79 | **75,43** | 68,52 |
  | bge-reranker-v2-m3 | 78,57 | 78,17 | 79,04 |
  | BiLSTM-ESIM | 55,38 | 51,07 | **63,25** |

  MedCPT-CE được huấn luyện trên log tìm kiếm PubMed (truy vấn dạng từ khóa) nên hợp với truy vấn từ khóa nhất. bge-reranker-v2-m3 gần như không bị ảnh hưởng. BiLSTM hưởng lợi từ narrative, vì narrative bổ sung các từ có vector thay cho "covid-19" bị OOV.
- **Dòng metadata (M1)** chèn trước abstract:
  - giúp MedCPT-CE: 68,79 → 72,08 với truy vấn câu hỏi;
  - gần như không đổi với bge-reranker-v2-m3 (78,57 → 78,52) và BiLSTM (55,38 → 55,04);
  - với LambdaMART CV 5-fold: 69,03 → 70,84.
- **Boost hậu kỳ theo độ trùng MeSH** (λ chọn bằng CV 5-fold) **không giúp hệ thống nào**: Δ từ −0,94 đến 0,00, không có ý nghĩa. MeSH của câu hỏi lấy bằng Automatic Term Mapping có nhiễu, và chỉ 40% bài ứng viên có MeSH.
- Chưa chạy các biến thể GPT về metadata, tiêu chí y khoa và xáo thứ tự ứng viên. Dòng Q-q và tiêu chí chung của GPT trong bảng E2 chỉ tái sử dụng E1, không phải một lần chạy độc lập. Không suy ra tác động metadata hay độ ổn định vị trí của GPT từ các kết quả này.

### 5.4 Nhãn thiếu (E3) — `report/tables/e3_labels.md`, hình `fig_e3_*`

- **TREC-COVID:** với nhãn tới hết vòng 1, BM25 chỉ có Judged@10 ≈ 9% và nDCG@10 = 5,7, so với 57,8 khi dùng nhãn đầy đủ. Đây là trường hợp nhãn nông cực đoan, vì kho vòng 1 nhỏ hơn nhiều so với kho bản tháng 7.
- **nDCG@10 condensed** (bỏ bài chưa có nhãn) cho BM25 là 37,5 / 48,7 / 61,5 / 63,7 khi dùng nhãn tới hết vòng 1 / 2 / 3 / 4.
- **TREC-COVID, Kendall τ giữa thứ hạng 12 hệ thống**, gồm GPT-6 Luna, khi chấm bằng nhãn nông so với nhãn đầy đủ (30 topic):

  | Nhãn tới hết vòng | τ (nDCG@10) | Cặp hệ thống đổi chỗ | τ (condensed) |
  |---|---:|---:|---:|
  | 1 | 0,52 | 16/66 | 0,61 |
  | 2 | 0,48 | 17/66 | 0,64 |
  | 3 | 0,70 | 10/66 | 0,79 |
  | 4 | 0,94 | 2/66 | 0,94 |

  Với nhãn tới vòng 1–2, khoảng một phần tư số cặp hệ thống đảo thứ tự; condensed cải thiện mức tương đồng ở ba vòng đầu. Riêng GPT-6 Luna trên 30 topic này, nDCG@10 thường ở vòng 1 là 9,36, condensed 41,13, so với 83,62 khi dùng nhãn đầy đủ. Đây là ảnh hưởng của thay đổi bộ nhãn trên cùng kết quả đã lưu, không phải mô hình được chạy lại.
- **SciFact-Open** (190 claim có bằng chứng ở cả hai bộ nhãn; 11 hệ thống, chưa có GPT): τ = 0,78, 6 cặp hệ thống đổi chỗ.
  - Mọi cross-encoder được cộng nhiều hơn BM25 (+1,44), LambdaMART (+2,11) và BiLSTM-ESIM (+2,07) khi chấm bằng nhãn đã soát: từ +3,50 (MedCPT-CE) đến +6,76 (bge-reranker-large).
  - LambdaMART tụt từ hạng 4 xuống hạng 6; bge-reranker-large lên từ 7 lên 5.
  - Kết quả này khớp với nhận định của BEIR (phân tích Hole@10): nhãn gom từ hệ thống từ vựng phạt oan các hệ thống ngữ nghĩa.

### 5.5 Chi phí và tốc độ (E4) — `report/tables/e4_cost.md`, hình `fig_e4_pareto.png`

Đo trên Tesla T4 (Kaggle), mỗi truy vấn 100 ứng viên. USD quy theo giá thuê T4 0,35 USD/giờ (ước lượng).

| Reranker | p50 (ms) | USD / 1.000 truy vấn | nDCG@10 TB 3 bộ |
|---|---:|---:|---:|
| BiLSTM-ESIM | 57 | 0,006 | 51,38 |
| MedCPT-CE | 643 | 0,063 | 61,02 |
| bge-reranker-base | 734 | 0,071 | 57,24 |
| mxbai-rerank-base (fp32) | 1.742 | 0,170 | 63,52 |
| bge-reranker-large | 2.247 | 0,217 | 60,75 |
| bge-reranker-v2-m3 | 2.275 | 0,220 | 62,08 |
| MonoT5-base (fp32) | 4.318 | 0,418 | 60,79 |
| Qwen3-Reranker-4B (2 T4) | 25.042 | 2,484 | 67,24 |
| GPT-6 Luna (API) | 28.914 | 5,614 | 67,94 |

Biên Pareto theo chi phí và chất lượng trung bình của các hệ thống local gồm BM25, MedCPT-CE, mxbai-rerank-base và Qwen3-Reranker-4B. GPT-6 Luna bổ sung một điểm có chất lượng cao hơn và chi phí cao hơn; chênh lệch nhỏ với Qwen3 chưa được kiểm định riêng. Giá GPU là quy đổi ước lượng, còn chi phí API tính theo token từ log; hai cách tính cần được phân biệt khi diễn giải.

**GPT-6 Luna, E1:** chi phí tính từ token sử dụng và bảng giá trong cấu hình là **3,7784 USD** cho 673 truy vấn, tương đương **5,6142 USD / 1.000 truy vấn**. Độ trễ tuần tự mỗi truy vấn: p50 **28,9 giây**, p95 **43,3 giây**, p99 **50,5 giây**; đây là tổng thời gian các cửa sổ API, không phải tổng thời gian chạy cả bộ khi xử lý song song. Số liệu lấy từ `results/api_logs/gpt_small__*.jsonl` và `results/e4/e4.json`; chưa bao gồm các lệnh kiểm tra kết nối rất nhỏ. Jev chưa chạy.

## 6. So với kết quả công bố

Đặt cạnh 15 dòng của Abdallah et al. (2025) (bảng `e1_main.md`, hình `fig_e1_ranking.png`, cùng BM25 top-100):

- **SciFact.** GPT-6 Luna (79,77) có điểm cao nhất trong bảng hiện tại, tiếp theo là MedCPT-CE (79,58) và Qwen3-Reranker-4B (79,35). Chênh lệch nhỏ giữa ba mô hình này chưa được kiểm định riêng nên không kết luận GPT vượt trội. MedCPT-CE chỉ khoảng 110M tham số vẫn trên InRanker-3B (78,31) và MonoT5-3B (76,57). LambdaMART (75,97) và BiLSTM-ESIM (72,30) đứng trên RankGPT gpt-3.5 (70,43).
- **NFCorpus.** GPT-6 Luna đạt 38,60, cao nhất trong các mô hình nhóm đã chạy, so với Qwen3-Reranker-4B 37,37. Dòng công bố MonoT5-3B đạt 38,97 và RankGPT gpt-4 đạt 38,47. Nhóm ưu tiên so bằng mức tăng so với BM25 vì nền BM25 lệch +1,43; không coi chênh lệch nhỏ với dòng công bố là bằng chứng vượt trội.
- **TREC-COVID.** GPT-6 Luna đạt 85,45, gần điểm công bố RankGPT gpt-4 (85,51); Qwen3-Reranker-4B đạt 85,00 và mxbai-rerank-base đạt 83,06. Điểm công bố ListT5-3B là 84,70. Lưu ý chênh lệch do cách nhập văn bản ở mục 5.1; chưa kiểm định riêng GPT-6 Luna với Qwen3.
- **LLM mã nguồn mở so với LLM qua API năm 2023.** Qwen3-Reranker-4B (chạy trên 2 GPU T4) đạt trung bình 3 bộ cao hơn RankGPT gpt-4 (67,24 so với 66,31). Thua ở TREC-COVID (−0,51) và NFCorpus (−1,10), nhưng hơn rõ ở SciFact (+4,40).
- **GPT-6 Luna:** trung bình ba bộ 67,94 so với Qwen3-Reranker-4B 67,24. Đây là so sánh điểm mô tả; kiểm định ở bảng E1 chỉ thực hiện với BM25 và bge-reranker-v2-m3. Jev chưa chạy.

## 7. Phân tích ca tốt / ca không tốt
Các ca được chọn theo chênh lệch nDCG@10 từng truy vấn, không được dùng để chỉnh prompt hay chọn mô hình. Bảng đầy đủ nằm ở `report/tables/error_cases.md`; thống kê có thể truy lại từ `results/error_analysis.json` và `results/e1/e1_per_query.json`.

| Bộ | GPT hơn BM25 | GPT kém BM25 | Bằng nhau |
|---|---:|---:|---:|
| TREC-COVID | 45 | 3 | 2 |
| NFCorpus | 142 | 40 | 141 |
| SciFact | 91 | 18 | 191 |

- **TREC-COVID, topic 9 — tác động tại Canada:** GPT tăng 64,2 điểm nDCG@10; bài đầu chuyển từ một tài liệu có nhãn 0 sang “Assessing the burden of COVID-19 in Canada” có nhãn liên quan. Ví dụ cho thấy chỉ trùng tên quốc gia và chủ đề COVID chưa bảo đảm kết quả đứng đầu đáp ứng đúng nhu cầu.
- **TREC-COVID, topic 6 — xét nghiệm nhanh:** GPT tăng 58,3 điểm; bài đầu BM25 có nhãn không liên quan, trong khi bài đầu sau rerank bàn về các xét nghiệm chẩn đoán và có nhãn liên quan.
- **TREC-COVID, topic 47 — kết cục sức khỏe ở trẻ em:** GPT giảm 7,5 điểm; tài liệu đầu mới chưa có nhãn. Không thể kết luận tài liệu này sai chỉ dựa vào điểm giảm. Đây cũng là lý do cần phân tích nhãn thiếu ở E3.
- **NFCorpus, truy vấn “coffee”:** GPT giảm 20,2 điểm; bài đầu thay từ “Coffee, tea, and mortality.” có nhãn liên quan sang một bài tổng quan chưa có nhãn. Truy vấn rất ngắn không nói rõ khía cạnh quan tâm, đồng thời bộ nhãn chưa bao phủ mọi bài có thể hữu ích.
- **SciFact, claim 831 — NF2/Merlin:** GPT tăng 100 điểm so với BM25; bài đầu sau rerank có nhãn bằng chứng. Trên SciFact vẫn có 18 claim bị giảm điểm, nên mức tăng trung bình không có nghĩa mọi truy vấn đều được cải thiện.

Các diễn giải trên dựa vào câu hỏi, tiêu đề và nhãn có sẵn; chúng không bổ sung phán quyết liên quan mới cho các tài liệu chưa được chấm.

Ví dụ từ demo (TREC-COVID, câu hỏi "what is the origin of COVID-19"):

- BM25 xếp đầu bài "What is the origin of SARS-CoV-2?" (`dv9m19yk`). Bài này trùng gần như toàn bộ câu chữ với truy vấn.
- MedCPT-CE đẩy một bài tổng quan về sự xuất hiện của COVID-19 lên đầu (`fqs40ivc`, tăng 7 bậc).
- Nhưng MedCPT-CE cũng giữ bài "Anesthesia and COVID-19" ở vị trí 2, một bài không bàn về nguồn gốc virus. Đây là ví dụ cho kiểu lỗi chỉ khớp chủ đề chung.

## 8. Demo RAG
Demo đã kiểm tra trong đợt này chạy bằng `python -m src.demo.offline_app` tại `http://127.0.0.1:7860`. Người dùng chọn một trong ba bộ và một trong 673 câu hỏi đã đánh giá, xem top-5 BM25 cạnh top-5 GPT-6 Luna, số bậc thay đổi, nhãn chuẩn và nDCG@10 từng truy vấn. Demo đọc kết quả đã lưu, không gọi API và không sinh câu trả lời mới. Chế độ RAG trực tiếp trong `src/demo/rag_app.py` vẫn là mã tham khảo; chưa được kiểm chứng từ đầu đến cuối trong môi trường hiện tại và không thuộc đợt không phát sinh phí này.

## 9. Kết luận và hạn chế
Giữ cố định ứng viên cho phép tách tác động của reranker khỏi bước tìm kiếm ban đầu. GPT-6 Luna có chất lượng trung bình cao nhất trong các hệ thống nhóm đã chạy, trong khi MedCPT-CE và mxbai-rerank-base tạo các lựa chọn local có chi phí quy đổi thấp hơn. BiLSTM-ESIM cho kết quả âm trên hai bộ, nhưng kết quả này giúp nhận diện hạn chế của embedding cố định, từ ngoài từ vựng và chuyển miền. Phân tích nhãn thiếu cho thấy điểm và thứ hạng hệ thống phụ thuộc đáng kể vào độ phủ nhãn; vì vậy cần báo cả thiết lập nhãn, không chỉ một điểm nDCG.

Các hạn chế của bản hiện tại:
- **Nhiễm dữ liệu:** các bộ công khai từ 2020–2022, nên GPT có thể đã thấy chúng.
- **Ít topic:** TREC-COVID chỉ có 50 topic, nên khoảng tin cậy rộng.
- **Nhãn vẫn còn lỗ:** pool của SciFact-Open chỉ từ 4 hệ thống, và repo không phát hành cặp âm.
- **Nhãn NFCorpus** sinh tự động từ link, nên có nhiễu.
- **Lệch nền NFCorpus** so với bài báo (+1,43 điểm).
- **Phạm vi GPT:** chưa chạy thử nghiệm metadata/tiêu chí/xáo thứ tự, SciFact-Open hoặc cascade và thay đổi số ứng viên; không có kết luận GPT cho các phần này.
- **Ablation:** hai biến thể tách thành phần BiLSTM v2 chỉ có một seed. Chưa hoàn tất các seed còn lại vì thiếu embedding/checkpoint gốc và quyền truy cập GPU Kaggle trong checkout hiện tại.
- **Tái chạy toàn bộ pipeline:** bộ đọc dữ liệu, đánh giá và demo offline đã phục hồi; metadata xử lý sẵn, ID chia train/dev gốc và các file trọng số/embedding chưa có đầy đủ trong checkout. Kết quả huấn luyện lịch sử được giữ nguyên; chưa tuyên bố tái lập lại toàn bộ quá trình huấn luyện.
- **Sai khác với RankGPT:** prompt GPT dùng đầu ra JSON thay cho định dạng "[2] > [1]" của bản gốc.

## Tài liệu tham khảo
- Abdallah, A. et al. (2025). How Good are LLM-based Rerankers? An Empirical Analysis of State-of-the-Art Reranking Models. Findings of EMNLP. arXiv:2508.16757.
- Burges, C. (2010). From RankNet to LambdaRank to LambdaMART: An Overview. Microsoft Research Technical Report.
- Chen, Q. et al. (2017). Enhanced LSTM for Natural Language Inference. ACL. arXiv:1609.06038.
- Jin, Q. et al. (2023). MedCPT: Contrastive Pre-trained Transformers with Large-scale PubMed Search Logs for Zero-shot Biomedical Information Retrieval. Bioinformatics. arXiv:2307.00589.
- Lin, J. et al. (2021). Pyserini: A Python Toolkit for Reproducible Information Retrieval Research. SIGIR.
- Sakai, T. (2007). Alternatives to Bpref. SIGIR.
- Sun, W. et al. (2023). Is ChatGPT Good at Search? Investigating Large Language Models as Re-Ranking Agents. EMNLP. arXiv:2304.09542.
- Thakur, N. et al. (2021). BEIR: A Heterogeneous Benchmark for Zero-shot Evaluation of Information Retrieval Models. NeurIPS Datasets and Benchmarks. arXiv:2104.08663.
- Voorhees, E. et al. (2020). TREC-COVID: Constructing a Pandemic Information Retrieval Test Collection. SIGIR Forum. arXiv:2005.04474.
- Wadden, D. et al. (2020). Fact or Fiction: Verifying Scientific Claims. EMNLP.
- Wadden, D. et al. (2022). SciFact-Open: Towards open-domain scientific claim verification. Findings of EMNLP. arXiv:2210.13777.
- Zhang, Y. et al. (2019). BioWordVec, improving biomedical word embeddings with subword information and MeSH. Scientific Data.
- Zhuang, S. et al. (2024). A Setwise Approach for Effective and Highly Efficient Zero-shot Ranking with Large Language Models. SIGIR. arXiv:2310.09497.
