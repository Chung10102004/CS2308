# So sánh các thế hệ reranker cho truy xuất y sinh trên benchmark có nhãn sẵn

> **Nháp do Claude viết — nhóm cần đọc, sửa và chịu trách nhiệm nội dung.**
> Mọi con số lấy từ `results/` (sinh bằng `make report`) hoặc từ bảng của bài báo được trích (`src/eval/published.py`).
> Chỗ đánh dấu ⟦…⟧ sẽ điền sau khi chạy xong phần GPU/API.

## Tóm tắt

⟦Viết sau khi có đủ kết quả E1–E4.⟧

## 1. Giới thiệu

Mô hình ngôn ngữ lớn có thể trả lời câu hỏi y sinh trôi chảy nhưng vẫn bịa thông tin. Hướng phổ biến để giảm việc này là RAG (retrieval-augmented generation): truy xuất tài liệu liên quan rồi buộc mô hình trả lời dựa trên đó. Trong một hệ thống RAG, **reranker** là khâu quyết định những tài liệu nào thực sự được đưa vào ngữ cảnh. First-stage (ví dụ BM25) lấy về hàng trăm ứng viên, và reranker chọn ra vài tài liệu đầu.

Có nhiều thế hệ reranker: learning-to-rank trên đặc trưng thủ công, mạng LSTM đối sánh câu, cross-encoder dựa trên Transformer, LLM xếp hạng kiểu listwise, và gần đây là các mô hình quyết định chuyên dụng như Jev. Kết quả công bố cho từng thế hệ thường dùng ứng viên, kho và cách chấm khác nhau, nên khó so sánh trực tiếp. Ngoài ra, nhãn của các bộ đánh giá thường được gom theo pooling nên bị thiếu. Một reranker tìm ra bài liên quan nhưng chưa ai chấm sẽ bị tính là sai.

Đồ án trả lời bốn câu hỏi:

- **RQ1:** Trên cùng danh sách BM25 top-100, các reranker của nhóm (LambdaMART, BiLSTM-ESIM, MedCPT cross-encoder, GPT-6 và Jev) đứng ở đâu so với 40 biến thể đã công bố?
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
| R5 | GPT-6 Luna (listwise, toàn bộ top-100) và GPT-6.1 Sol (chỉ top-30 của Luna) | Prompt hoán vị của RankGPT; cửa sổ 20, bước 10; đoạn văn cắt 300 từ; đầu ra JSON qua structured outputs |
| R6 | Jev qua `jev-reranker` | Listwise và pointwise, `threshold=0` |

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

⟦BiLSTM-ESIM v2: chờ đủ 3 seed cho hai bản ablation⟧

⟦R5, R6 — chạy `make api-run`⟧

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
- ⟦2×2 tiêu chí, listwise/pointwise, thiên vị vị trí — cần API⟧

### 5.4 Nhãn thiếu (E3) — `report/tables/e3_labels.md`, hình `fig_e3_*`

- **TREC-COVID:** với nhãn tới hết vòng 1, BM25 chỉ có Judged@10 ≈ 9% và nDCG@10 = 5,7, so với 57,8 khi dùng nhãn đầy đủ. Đây là trường hợp nhãn nông cực đoan, vì kho vòng 1 nhỏ hơn nhiều so với kho bản tháng 7.
- **nDCG@10 condensed** (bỏ bài chưa có nhãn) cho BM25 là 37,5 / 48,7 / 61,5 / 63,7 khi dùng nhãn tới hết vòng 1 / 2 / 3 / 4.
- **TREC-COVID, Kendall τ giữa thứ hạng 9 hệ thống** khi chấm bằng nhãn nông so với nhãn đầy đủ (30 topic):

  | Nhãn tới hết vòng | τ (nDCG@10) | Cặp hệ thống đổi chỗ | τ (condensed) |
  |---|---:|---:|---:|
  | 1 | 0,28 | 13/36 | 0,67 |
  | 2 | 0,28 | 13/36 | 0,67 |
  | 3 | 0,56 | 8/36 | 0,78 |
  | 4 | 0,94 | 1/36 | 0,89 |

  Như vậy với nhãn nông, nDCG@10 thông thường đảo thứ tự hơn một phần ba số cặp. Bản condensed giảm đáng kể việc đảo này.
- **SciFact-Open** (190 claim có bằng chứng ở cả hai bộ nhãn): τ = 0,72, 5 cặp hệ thống đổi chỗ.
  - Mọi cross-encoder được cộng nhiều hơn BM25 (+1,44), LambdaMART (+2,11) và BiLSTM-ESIM (+2,07) khi chấm bằng nhãn đã soát: từ +3,50 (MedCPT-CE) đến +6,76 (bge-reranker-large).
  - LambdaMART tụt từ hạng 3 xuống hạng 5; bge-reranker-large lên từ 6 lên 4.
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

Biên Pareto của nhóm local gồm BM25, MedCPT-CE và mxbai-rerank-base; các model còn lại đều có một model khác vừa rẻ hơn vừa tốt hơn.

⟦R5, R6: chi phí thật từ `results/api_logs/`⟧

## 6. So với kết quả công bố

Đặt cạnh 15 dòng của Abdallah et al. (2025) (bảng `e1_main.md`, hình `fig_e1_ranking.png`, cùng BM25 top-100):

- **SciFact.** MedCPT-CE (79,58) đứng đầu toàn bảng, trên InRanker-3B (78,31) và MonoT5-3B (76,57) dù chỉ khoảng 110M tham số. LambdaMART (75,97) và BiLSTM-ESIM (72,30) đứng trên RankGPT gpt-3.5 (70,43).
- **NFCorpus.** Mọi reranker nằm trong khoảng hẹp 31–39 (nhãn tự động, truy vấn rất ngắn). Tốt nhất của nhóm là LambdaMART (35,67) và mxbai (35,48), ngang Cohere Rerank-v2 (36,36). Nhóm so bằng mức tăng so với BM25 vì nền BM25 lệch +1,43.
- **TREC-COVID.** mxbai-rerank-base đạt 83,06, gần với số của bài (84,00); bge-reranker-v2-m3 đạt 78,57. Các dòng mạnh nhất của bài (RankGPT gpt-4 85,51, ListT5-3B 84,70) vẫn cao hơn mọi reranker local của nhóm. Lưu ý chênh lệch do cách nhập văn bản ở mục 5.1.
- **LLM mã nguồn mở so với LLM qua API năm 2023.** Qwen3-Reranker-4B (chạy trên 2 GPU T4) đạt trung bình 3 bộ cao hơn RankGPT gpt-4 (67,24 so với 66,31). Thua ở TREC-COVID (−0,51) và NFCorpus (−1,10), nhưng hơn rõ ở SciFact (+4,40).
- ⟦GPT-6, Jev⟧

## 7. Phân tích ca tốt / ca không tốt
⟦Chọn 3–5 truy vấn mỗi nhóm từ `results/e1/e1_per_query.json`: reranker hơn BM25 nhiều nhất / kém nhất; ca Jev và GPT bất đồng; ca "sai" theo nhãn gốc nhưng đúng theo SciFact-Open.⟧

Ví dụ từ demo (TREC-COVID, câu hỏi "what is the origin of COVID-19"):

- BM25 xếp đầu bài "What is the origin of SARS-CoV-2?" (`dv9m19yk`). Bài này trùng gần như toàn bộ câu chữ với truy vấn.
- MedCPT-CE đẩy một bài tổng quan về sự xuất hiện của COVID-19 lên đầu (`fqs40ivc`, tăng 7 bậc).
- Nhưng MedCPT-CE cũng giữ bài "Anesthesia and COVID-19" ở vị trí 2, một bài không bàn về nguồn gốc virus. Đây là ví dụ cho kiểu lỗi chỉ khớp chủ đề chung.

## 8. Demo RAG
`make demo`: nhập câu hỏi, chạy BM25 top-k, chọn reranker, xem top-5 trước và sau rerank (kèm số bậc tăng/giảm), rồi GPT trả lời có trích dẫn [doc_id]. Demo không dùng để đánh giá định lượng.

## 9. Kết luận và hạn chế
- **Nhiễm dữ liệu:** các bộ công khai từ 2020–2022, nên GPT có thể đã thấy chúng.
- **Ít topic:** TREC-COVID chỉ có 50 topic, nên khoảng tin cậy rộng.
- **Nhãn vẫn còn lỗ:** pool của SciFact-Open chỉ từ 4 hệ thống, và repo không phát hành cặp âm.
- **Nhãn NFCorpus** sinh tự động từ link, nên có nhiễu.
- **Lệch nền NFCorpus** so với bài báo (+1,43 điểm).
- **Giá Jev** lấy từ nguồn thứ cấp.
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
