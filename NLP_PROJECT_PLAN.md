# BioRerank — Kế hoạch đồ án NLP (v2)

> Đồ án cuối kỳ môn **Chuyên đề nghiên cứu xử lý ngôn ngữ tự nhiên**.
> Đề tài khung: *RAG trên domain nhỏ, QA*. Trọng tâm là **khâu rerank** của RAG. Pipeline RAG chỉ dùng để **demo**.
> Người thực hiện code: Claude (toàn bộ). Các việc chỉ con người làm được nằm ở [mục 15](#15-việc-nhóm-phải-tự-làm).
> Trạng thái: **kế hoạch, chưa có code**. Cập nhật lần cuối: 06/11/2026.
> Bản cũ (BioASQ-MetaRR, có chấm tay): `NLP_PROJECT_PLAN_v1.md`. Lý do đổi: [mục 17](#17-nhật-ký-quyết-định).

---

## 0. Tóm tắt

Nhóm so sánh **sáu thế hệ reranker** trên ba bộ truy xuất y sinh của BEIR: **TREC-COVID, NFCorpus, SciFact**. Sáu reranker là LambdaMART, BiLSTM-ESIM, MedCPT cross-encoder, bge-reranker, GPT listwise và Jev (TypeSafe).

Mọi reranker xếp lại **cùng một danh sách BM25 top-100**, đúng thiết lập của bài so sánh Abdallah et al. (EMNLP Findings 2025). Bài đó đã có 22 phương pháp với 40 biến thể. Vì vậy kết quả của nhóm **đặt thẳng vào bảng đã công bố**, không phải chạy lại các dòng có sẵn.

Ba nguyên tắc:

1. **Không chấm tay, không dùng LLM làm người chấm.** Mọi nhãn đều có sẵn: do NIST chấm, do chuyên gia chú thích, hoặc sinh tự động từ link.
2. **Tái lập trước, so sau.** Chạy lại BM25 và bge-reranker-v2-m3. Chỉ khi số khớp với bài báo thì mới đặt kết quả mới cạnh bảng.
3. **Chỉ chạy những dòng bài báo chưa có.**

Ngoài bảng chính còn ba phân tích:

- metadata và cách diễn đạt truy vấn, dùng các trường câu hỏi do NIST viết sẵn;
- ảnh hưởng của nhãn thiếu, dùng nhãn chuyên gia soát lại của **SciFact-Open** và qrels theo từng vòng của TREC-COVID;
- chi phí và tốc độ.

---

## 1. Yêu cầu của môn

| # | Yêu cầu | Đáp ứng ở |
|---|---|---|
| 1 | Giới thiệu bài toán | Mục 2, mục 11 |
| 2 | Phân tích ngữ liệu | Mục 4.7 |
| 3 | Phương pháp tiếp cận (**ít nhất LSTM**) | Mục 5, 6. LSTM là **BiLSTM-ESIM reranker** (R2) |
| 4 | So sánh kết quả công bố gần đây | Mục 10. Bảng của Abdallah et al. 2025, cùng thiết lập |
| 5 | Giải thích trường hợp mô hình tốt / không tốt | Mục 7 (phân tích), mục 11 |

---

## 2. Ý tưởng và đóng góp

### 2.1 Ý tưởng trong một câu
Đặt các reranker mà bảng so sánh lớn nhất hiện có còn thiếu vào đúng bảng đó, với cùng ứng viên và cùng cách chấm. Các reranker này gồm: một mô hình LSTM, một mô hình truyền thống, một cross-encoder chuyên y sinh, một LLM đời mới và một mô hình quyết định chuyên dụng (Jev). Sau đó phân tích khi nào chúng thắng hoặc thua, và việc nhãn thiếu làm lệch kết luận ra sao.

### 2.2 Hạ tầng và đóng góp

| | Nội dung | Cách làm |
|---|---|---|
| **Hạ tầng** (phải có, không phải đóng góp) | BM25 top-100, gọi reranker, tính metric, demo RAG | Dùng công cụ có sẵn: Pyserini, `ir_measures`, HF Transformers, OpenAI SDK, `jev-reranker`, Gradio |
| **C1. Bảng so sánh** ⭐ | 5 reranker mới (R1 LambdaMART, R2 BiLSTM-ESIM, R3 MedCPT-CE, R5 GPT hiện hành, R6 Jev) đặt vào bảng 40 biến thể của Abdallah et al. 2025; R0 và R4 dùng để tái lập | Chạy trên BM25 top-100 dùng chung |
| **C2. Metadata** | Truy vấn dạng từ khóa, câu hỏi hay câu hỏi kèm narrative; có hay không metadata tài liệu; tiêu chí chung hay tiêu chí lấy từ narrative cho Jev/GPT | TREC-COVID, dùng trường của NIST |
| **C3. Nhãn thiếu** | Thứ hạng các reranker thay đổi thế nào khi chấm bằng nhãn gốc so với nhãn đã soát lại | SciFact-Open (chuyên gia) và qrels theo vòng của TREC-COVID (NIST) |
| **C4. Chi phí và tốc độ** | USD/1.000 câu, độ trễ, Pareto chi phí–chất lượng | Log mọi lệnh gọi |

### 2.3 Câu hỏi nghiên cứu
- **RQ1 — Thế hệ reranker:** trên cùng BM25 top-100, BiLSTM-ESIM, LambdaMART, MedCPT-CE, GPT đời hiện tại và Jev đứng ở đâu so với 40 biến thể đã công bố?
  - Reranker chuyên y sinh (MedCPT-CE) có thắng reranker tổng quát cùng cỡ (bge) không?
  - GPT hiện tại so với gpt-3.5 và gpt-4 năm 2023 (RankGPT) ra sao?
- **RQ2 — Metadata và cách diễn đạt truy vấn:** câu hỏi đầy đủ, narrative và metadata tài liệu (MeSH, loại bài, năm) giúp reranker thế hệ nào, giúp bao nhiêu?
- **RQ3 — Nhãn thiếu:** chấm bằng nhãn gốc (thiếu) thì thứ hạng reranker có khác chấm bằng nhãn đã soát lại không? Reranker nào bị "phạt oan" nhiều nhất?
- **RQ4 — Chi phí và tốc độ:** với cùng mức chất lượng, nên dùng Jev, GPT hay mô hình local?

### 2.4 Câu đóng góp (dùng cho tiểu luận và slide)
> *"Chúng tôi đánh giá sáu thế hệ reranker, từ LambdaMART và BiLSTM-ESIM đến GPT và Jev, trên ba bộ truy xuất y sinh của BEIR với cùng danh sách ứng viên BM25 top-100 như bảng so sánh 40 biến thể của Abdallah et al. (2025), nên kết quả so trực tiếp được với các con số đã công bố. Chúng tôi chỉ ra metadata và tiêu chí y khoa giúp reranker nào, việc dùng nhãn thiếu làm thay đổi kết luận so sánh ra sao (dựa trên nhãn chuyên gia soát lại của SciFact-Open), và ở mức chi phí nào một mô hình quyết định chuyên dụng (Jev) đáng dùng hơn LLM tổng quát. Toàn bộ đánh giá dùng nhãn có sẵn, không có chấm tay hay LLM chấm."*

---

## 3. Ràng buộc và tài nguyên

| Loại | Chi tiết |
|---|---|
| LLM API | **Chỉ có OpenAI GPT.** Chỉ dùng làm **reranker** (R5) và sinh câu trả lời trong **demo**. **Không dùng để chấm** |
| Jev | TypeSafe Jev, gọi qua thư viện [`jev-reranker`](https://github.com/hotchpotch/jev-reranker) (MIT, cần API key TypeSafe) |
| PubMed | NCBI E-utilities (`efetch`, `esearch`). Chỉ dùng để lấy MeSH cho tài liệu TREC-COVID (mục 4.5). Có API key thì gọi được 10 request/giây |
| Compute | CPU local (16 nhân, 15 GB RAM). **GPU: Kaggle** (Tesla T4, tài khoản `hoangducchung`, tối đa 2 phiên GPU cùng lúc), điều khiển bằng Kaggle CLI qua `scripts/kaggle_job.py` / `kaggle_pipeline.py` |
| Java | JRE 21 (`/usr/lib/jvm/java-21-openjdk-amd64`) chạy được Pyserini 2.4 — đã xác minh |
| Python | 3.12, môi trường `.venv` (`python3 -m venv`; máy không có `uv`), thư viện ghim trong `requirements.txt` |
| Đĩa | Dữ liệu thô khoảng 1,8 GB; index SciFact-Open 522 MB |
| Khóa API | **`API.json`** (mẫu `API.example.json`, đã gitignore): `OPENAI_API_KEY`, `TYPESAFE_API_KEY`, `NCBI_API_KEY` (tùy chọn), `NCBI_EMAIL` (tùy chọn). Kiểm tra bằng `make check-api` |
| Model GPT | `gpt-6-luna` (R5s, effort `none`, toàn bộ top-100) và `gpt-6.1-sol` (R5l, effort `low`, chỉ xếp lại top-30 của R5s, như RankGPT gpt-4). Giá trong `configs/pricing.yaml` (06/11/2026) |
| Ngân sách | Đặt giới hạn chi tiêu trên dashboard của OpenAI và TypeSafe. Code có chặn chi phí (xem mục 16) |

---

## 4. Dữ liệu

Không cần đăng ký. Mọi bộ đều tải công khai qua `ir_datasets`, HF `BeIR/*` hoặc repo gốc.

### 4.1 Ba bộ chính (bảng E1)
Số liệu lấy từ [BEIR](https://arxiv.org/abs/2104.08663), bảng 1.

| Bộ | Truy vấn test | Kho | Bài đúng TB/truy vấn | Mức nhãn | Train | Ai gán nhãn |
|---|---:|---:|---:|---|---|---|
| **TREC-COVID** | 50 | 171.332 | 493,5 | 3 mức (0/1/2) | Không | **NIST**, tổng 69.318 nhãn qua 5 vòng |
| **NFCorpus** | 323 | 3.633 | 38,2 | 3 mức | 110.575 cặp; dev 324 câu | **Tự động** từ cấu trúc link của NutritionFacts.org |
| **SciFact** | 300 | 5.183 | 1,1 | Nhị phân | 920 cặp (809 claim) | **Chuyên gia** chú thích |

Ghi chú:
- **TREC-COVID:** bản BEIR lấy trường **`question`** làm văn bản truy vấn (đã kiểm trên HF `BeIR/trec-covid`, ví dụ topic 1: *"what is the origin of COVID-19"*). Hai trường `query` (từ khóa) và `narrative` lấy từ file topic gốc của NIST.
- **NFCorpus:** ID tài liệu dạng `MED-xxx`, văn bản là abstract PubMed. Nhãn sinh tự động nên có nhiễu, nhưng không cần người kiểm.
- **SciFact:** nhãn tập test gốc bị ẩn. BEIR dùng 300 claim có nhãn làm split test; **đã xác minh** đó chính là `claims_dev` gốc (300/300 ID và văn bản trùng). Chỉ 188/300 claim có bằng chứng; BEIR vẫn có qrels cho cả 300.

### 4.2 SciFact-Open (cho RQ3)
Nguồn: [Wadden et al., EMNLP Findings 2022](https://arxiv.org/abs/2210.13777), repo [`dwadden/scifact-open`](https://github.com/dwadden/scifact-open).

- **279 claim**, lấy từ tập test của SciFact (đã loại 21 trên 300).
- Kho khoảng **500K abstract** (S2ORC). Trường `scifact_orig` đánh dấu bài thuộc kho SciFact gốc.
- **Nhãn:** bằng chứng gốc của SciFact (lấy qua trích dẫn) có **209** cặp claim–abstract.
  - Nhóm tác giả gom các dự đoán hàng đầu của **4 hệ thống** thành pool.
  - Chuyên gia chấm từng cặp trong pool, sau đó **người thứ hai kiểm tra lại**.
  - Kết quả tìm thêm **251** cặp, tổng cộng **460**. Như vậy hơn một nửa số bằng chứng bị thiếu trong nhãn gốc.
- Trường **`provenance` = `"citation"` | `"pooling"`** cho phép tách ngay:
  - `qrels_orig` = các cặp `citation`;
  - `qrels_open` = toàn bộ cặp.
- Repo có thư mục `prediction` chứa dự đoán của các model dùng để gom pool.
- **Đã xác minh:** repo **không** phát hành các cặp đã chấm nhưng không phải bằng chứng, nên không tính được Judged@10 trên SciFact-Open. E3 trên bộ này chỉ dùng nDCG@10 và R@10.
- Đã kiểm khi tải: 190 claim có bằng chứng theo nhãn gốc, 206 theo nhãn đã soát; 81 claim được thêm bằng chứng.

### 4.3 TREC-COVID theo từng vòng (cho RQ3)
- File qrels của NIST có cột `iteration` ghi **vòng chấm của từng cặp**, có cả vòng lẻ như 1.5 ([trang dữ liệu NIST](https://ir.nist.gov/trec-covid/data.html)).
- `qrels_shallow(r)` = các cặp được chấm tới hết vòng r (r = 1..4); `qrels_full` = qrels test của BEIR. Tất cả giới hạn trong **30 topic có từ vòng 1** (đã xác minh) và trong kho BEIR.
- Đã xác minh: 69.318 nhãn; không có cặp nào mang hai nhãn khác nhau; nhãn tới vòng 1 có 7.569 cặp (2.038 liên quan), nhãn đầy đủ trên 30 topic đó có 43.576 cặp (16.164 liên quan).
- Kho vòng 1 nhỏ hơn kho BEIR (bản 2020-07-16) nhiều, nên với nhãn vòng 1 BM25 chỉ có Judged@10 ≈ 9%. Vì vậy E3 báo thêm **nDCG@10 condensed** (bỏ bài chưa có nhãn trước khi chấm, Sakai 2007) và cả đường cong theo r = 1..4.

### 4.4 Chia tập và chống rò rỉ
- **test:** split test của BEIR cho 3 bộ, và 279 claim của SciFact-Open. **Không bao giờ dùng để chỉnh tham số.**
- **dev:** 324 câu dev của NFCorpus, cộng 20% số claim train của SciFact (giữ lại, chia ngẫu nhiên với seed 0). Dùng để chọn siêu tham số, prompt và ngưỡng.
- **train** (cho R1, R2): train NFCorpus cộng 80% còn lại của train SciFact. **TREC-COVID không có train**, nên R1 và R2 chạy zero-shot trên bộ này.
- **Kiểm tra rò rỉ:**
  - ID claim của SciFact train không được trùng với SciFact test (BEIR) hay SciFact-Open.
  - Kiểm tra câu gần trùng giữa train và test: TF-IDF cosine > 0,9 thì loại câu đó khỏi train. Ghi lại số câu đã loại.

### 4.5 Metadata tài liệu (TREC-COVID)
- Đọc `metadata.csv` của CORD-19 (bản khớp với kho BEIR) theo `cord_uid`. Lấy các trường `journal`, `publish_time`, `source_x`, `pubmed_id`.
- Với các bài có `pubmed_id`, gọi `efetch` (`db=pubmed`, `retmode=xml`, 200 PMID mỗi request) để lấy MeSH (descriptor, major) và `pub_types`.
- **Báo cáo tỷ lệ phủ:** bao nhiêu % bài trong top-100 có `pubmed_id`, có MeSH, có loại bài. Bài thiếu metadata thì đánh cờ, không bỏ.
- Toàn bộ metadata này do NLM/CORD-19 cung cấp sẵn, **không cần kiểm tay**.

### 4.6 Metadata câu hỏi (TREC-COVID)
- **Lấy trực tiếp từ topic của NIST:** `query` (từ khóa), `question` (câu hỏi), `narrative` (mô tả thế nào là liên quan). Không dùng GPT để trích.
- **Ánh xạ câu hỏi sang MeSH** (cho đặc trưng "độ trùng MeSH" của R1) bằng Automatic Term Mapping của PubMed. Gọi `esearch` rồi đọc `TranslationSet`. Cách này **tất định, không dùng LLM**. **TODO: xác minh** định dạng output.

### 4.7 Phân tích ngữ liệu (mục 2 của tiểu luận)
- Độ dài truy vấn và tài liệu; số bài đúng mỗi truy vấn; phân bố mức nhãn. So sánh giữa 3 bộ.
- **Độ trùng từ** giữa truy vấn và bài đúng, so với bài sai trong BM25 top-100. Chỉ số này giải thích vì sao BM25 mạnh hoặc yếu ở mỗi bộ.
- **Recall@100 của BM25** (cận trên cho mọi reranker).
  - Lưu ý TREC-COVID có Recall@100 thấp (Pyserini báo 0,109) vì mỗi topic có khoảng 494 bài đúng. Đây không phải dấu hiệu BM25 kém.
- **Judged@100** của BM25 top-100: tỷ lệ ứng viên đã có nhãn.
- TREC-COVID: tỷ lệ phủ metadata (mục 4.5); phân bố nhánh MeSH, loại bài, năm.
- **Nhãn thiếu:**
  - SciFact-Open: phân bố số bằng chứng `citation` và `pooling` trên mỗi claim.
  - TREC-COVID: số nhãn theo từng vòng.

### 4.8 Bản quyền
Mỗi bộ có giấy phép riêng (BEIR, CORD-19, NFCorpus, SciFact, SciFact-Open). **TODO: đọc giấy phép trước khi phát hành.** Nhóm chỉ phát hành **file run (TREC format), metadata theo ID và script**, không phát hành lại văn bản.

---

## 5. Pipeline

```
Truy vấn (+ metadata câu hỏi ở E2)
   │
   ▼
BM25 Pyserini (flat) → top-100 CỐ ĐỊNH, dùng chung cho mọi reranker
   │
   ▼
RERANKER R0–R6 (+ reranker local phụ ở E3) ──► thứ hạng top-100 ──► chấm nDCG@10 bằng qrels có sẵn
   │
   └──► (chỉ trong demo) top-5 → GPT sinh câu trả lời có trích dẫn [doc_id]
```

**Demo RAG** (không đánh giá định lượng):
- App Gradio. Kho dùng TREC-COVID hoặc SciFact.
- Người dùng nhập câu hỏi. App hiện **top-5 trước và sau khi rerank** cạnh nhau, rồi GPT trả lời có trích dẫn.
- Chuẩn bị sẵn 3–5 câu hỏi minh họa cho slide, gồm ca reranker sửa đúng và ca reranker làm sai.

---

## 6. Mô hình

### 6.1 Các reranker

| ID | Thế hệ | Reranker | Cấu hình chính | Có trong bảng Abdallah 2025? |
|---|---|---|---|---|
| R0 | — | **BM25** (Pyserini flat, `beir-v1.0.0-<bộ>.flat`) | top-100, giữ nguyên thứ tự | Có → **tái lập** |
| R1 | Truyền thống | **LambdaMART** (LightGBM `LGBMRanker`, `lambdarank`) | Đặc trưng: điểm và hạng BM25, TF-IDF cosine, MedCPT bi-encoder cosine (chỉ tính trên top-100), độ trùng từ, độ dài, khớp tiêu đề. Ở M1 thêm (TREC-COVID): năm, loại bài, độ trùng MeSH câu hỏi–bài. Train trên train NFCorpus + SciFact, chỉnh trên dev | Không → **mới** |
| R2 | **LSTM** | **BiLSTM-ESIM** (PyTorch) | Embedding BioWordVec 200 chiều (tải một lần rồi cắt theo vocab). BiLSTM mã hóa 1 lớp, 200 chiều mỗi hướng → soft alignment → BiLSTM tổng hợp → avg+max pool → MLP → điểm. Đầu vào: truy vấn + tiêu đề + abstract, cắt còn 256 token. Loss softmax listwise với 1 bài đúng (nhãn ≥ 1) và 7 bài sai lấy từ BM25 top-100. Adam, early stopping theo nDCG@10 trên dev. Seed 0/1/2 | Không → **mới** |
| R3 | Cross-encoder y sinh | `ncbi/MedCPT-Cross-Encoder` | Zero-shot | Không → **mới** |
| R4 | Cross-encoder tổng quát | `BAAI/bge-reranker-v2-m3` | Zero-shot | Có → **tái lập** |
| R5 | LLM | **GPT listwise** (kiểu RankGPT) | Cửa sổ 20, bước trượt 10 trên top-100, tức **9 lệnh gọi mỗi truy vấn**. Kết quả là hoán vị ID dạng JSON; ID bị thiếu hoặc trùng thì nối vào cuối. Temperature 0 nếu model hỗ trợ. Hai cỡ `gpt_small` và `gpt_large` | RankGPT có gpt-3.5/gpt-4 (2023) → **mới** với GPT hiện hành |
| R6 | Mô hình quyết định | **Jev** qua `jev-reranker` 0.1.2 | Chế độ listwise (mặc định) và pointwise; `threshold=0` khi rerank. Top-100 có thể vượt `split_state_budget` (26k) nên Jev tự chia nhóm; ghi lại số request thật. Tokenizer mặc định của thư viện (`google/embeddinggemma-300m`) là repo bị khóa trên HF, nên chia nhóm bằng `length_fn` ước lượng 4 ký tự/token. Tên model thật lấy từ `detail.resolved_models` | Không → **mới** |

**Reranker local phụ** (chỉ dùng cho E3, để đủ số hệ thống tính Kendall τ, và làm thêm điểm kiểm tra tái lập): MonoT5-base, bge-reranker-base, bge-reranker-large, mxbai-rerank-base. Cả bốn đều có trong bảng Abdallah 2025. Chạy qua Rankify hoặc HF, theo cài đặt mặc định.

Model ID của GPT để trong `configs/models.yaml` (`gpt_small`, `gpt_large`). **Điền model ID hiện hành khi bắt đầu**, lấy từ trang models của OpenAI.

### 6.2 Các mức metadata (chỉ TREC-COVID, E2)
- **Dạng truy vấn:** `Q-kw` (trường `query`) · `Q-q` (trường `question`, **mặc định của BEIR**, dùng cho E1) · `Q-qn` (`question` + `narrative`).
- **Metadata tài liệu:**
  - **M0:** chỉ văn bản.
  - **M1:** thêm metadata tài liệu.
    - Với R2–R6: chèn dòng `[Journal: …] [Year: …] [Type: …] [MeSH: …]` trước abstract.
    - Với R1: metadata nằm trong đặc trưng.
- **Boost hậu kỳ,** áp dụng đồng đều cho mọi reranker: `score' = z(score) + λ · overlap_MeSH`.
  - **Đã chọn:** TREC-COVID không có dev nên λ ∈ {0; 0,1; 0,25; 0,5; 1; 2} được chọn bằng **CV 5-fold theo topic** (chọn trên 4 fold, chấm trên fold còn lại).
  - R1 ở M1 cũng dùng CV 5-fold trên TREC-COVID, vì train NFCorpus/SciFact không có metadata nên không học được trọng số metadata.
  - MeSH của câu hỏi lấy bằng Automatic Term Mapping của PubMed; đôi khi có từ nhiễu (ví dụ "persons", "volition").

### 6.3 Tiêu chí cho Jev và GPT
Dùng cùng một nội dung tiêu chí cho Jev (`instruction`) và GPT (prompt). **Định dạng `instruction` của Jev phải xác minh theo README:** một dict gồm `instructions` và `criteria` với các nhánh `true`/`false`.

- **Tiêu chí chung (generic),** dùng cho bảng chính E1:
  - instructions: *"Judge whether the passage is relevant to the query."*
  - true: *"The passage is relevant to the query."*
  - false: *"The passage is not relevant to the query."*
- **Tiêu chí theo narrative (TREC-COVID, E2):**
  - instructions: *"Judge whether the abstract is relevant to the topic."*
  - true: **trường `narrative` của NIST cho topic đó.**
  - false: *"The abstract does not meet the description above."*
  - Không cần tự viết tiêu chí, nên tránh thiên vị do người viết prompt.
- **Tiêu chí y khoa cố định (NFCorpus, SciFact, E2):**
  - instructions: *"You are screening PubMed abstracts for a biomedical search system. Judge whether the abstract provides evidence relevant to the query."*
  - true: *"The abstract addresses the same entities as the query (disease, gene, drug, intervention, population) and reports findings, definitions or facts relevant to it."*
  - false: *"The abstract is off-topic, only shares background terms, concerns a different entity or population, or contains nothing relevant."*

---

## 7. Thí nghiệm

| # | Thí nghiệm | Cấu hình | Metric | RQ |
|---|---|---|---|---|
| **E0** | **Tái lập** | R0 BM25 và R4 bge-reranker-v2-m3 trên 3 bộ, cùng top-100. Thêm 4 reranker local phụ làm điểm kiểm tra thứ hai | nDCG@10 so với bảng Abdallah 2025. **Đạt khi:** BM25 lệch ≤ 0,5 điểm (riêng NFCorpus xem mục 10.3); bge lệch ≤ 1 điểm. Lệch hơn thì phải tìm nguyên nhân (trường truy vấn, cắt độ dài, fp16, phiên bản index) **trước khi chạy E1** | C1 |
| **E1** | **Bảng chính** | R0–R6 × 3 bộ, dạng truy vấn `Q-q`, M0, tiêu chí chung | nDCG@10 (chính, để so bài báo), MRR@10, Recall@10, **Judged@10**. Kiểm định so với R0 và so với R4 | RQ1 |
| **E2** | Metadata và tiêu chí | (a) TREC-COVID: {`Q-kw`, `Q-q`, `Q-qn`} × {M0, M1} cho R1–R6. (b) Jev/GPT 2×2: {tiêu chí chung, tiêu chí narrative/y khoa} trên cả 3 bộ. (c) Jev listwise so với pointwise. (d) **Thiên vị vị trí:** xáo thứ tự ứng viên 3 lần trên 50 topic TREC-COVID và 100 câu NFCorpus, đo Kendall τ giữa các lần | Như E1, cộng độ ổn định | RQ2 |
| **E3** | **Nhãn thiếu** | (a) **SciFact-Open:** BM25 top-100 trên kho 500K → R0–R6 và 4 reranker phụ → chấm bằng `qrels_orig` và `qrels_open`. (b) **TREC-COVID:** chấm lại mọi run của E1 bằng `qrels_shallow` và `qrels_full`. (c) Judged@10 của từng hệ thống | Δ nDCG@10 mỗi hệ thống; **Kendall τ** giữa thứ hạng hệ thống của hai bộ nhãn; hệ thống bị đổi hạng nhiều nhất | RQ3 |
| **E4** | Chi phí và tốc độ | Mọi reranker; cascade; quy mô k (xem mục 9) | USD/1.000 câu, p50/p95/p99, thông lượng, tỷ lệ lỗi | RQ4 |

**Quy tắc chấm cho E3(a):**
- Số chính tính trên **giao** của hai tập claim: các claim có ít nhất 1 bằng chứng trong cả hai bộ nhãn.
- Thêm số trên toàn bộ claim hợp lệ của từng bộ nhãn.

**Giả thuyết đối chiếu cho E3:** BEIR đã thấy nhãn thiếu trên TREC-COVID phạt hệ dense nặng hơn BM25 (mục 10.2). Kỳ vọng là các reranker neural và LLM cũng bị `qrels_orig` phạt nặng hơn BM25.

**Phân tích (cho mục 5 của tiểu luận):**
- Theo từng bộ; theo độ dài truy vấn; theo **độ trùng từ** truy vấn–bài đúng (reranker nào thắng khi độ trùng thấp).
- Feature importance của LambdaMART.
- BiLSTM-ESIM: tỷ lệ OOV, ảnh hưởng của việc cắt 256 token, so sánh trong miền (NFCorpus, SciFact) với zero-shot (TREC-COVID).
- Các ca Jev và GPT bất đồng; các ca metadata hoặc narrative giúp và hại.
- Các ca reranker **đẩy bài đúng xuống** so với BM25.
- Các ca "sai" theo `qrels_orig` nhưng thành đúng theo `qrels_open`.
- Chọn 3–5 ví dụ cụ thể cho mỗi nhóm.

---

## 8. Đánh giá

- **Metric:** `ir_measures` (hoặc `pytrec_eval`) cho nDCG@10, MRR@10, Recall@k, Judged@10.
  - Dùng đúng nDCG@10 như BEIR và Abdallah 2025, nhãn nhiều mức giữ nguyên mức.
  - Chỉ so với số công bố bằng **nDCG@10**.
- **Không có LLM-judge. Không có chấm tay.** Mọi nhãn lấy từ qrels có sẵn (mục 4).
- **Kiểm định ý nghĩa thống kê:**
  - Paired bootstrap (10.000 lần lấy mẫu) hoặc randomization test trên điểm từng truy vấn.
  - Hiệu chỉnh Holm khi so nhiều hệ thống với một baseline.
  - Đánh dấu * khi p < 0,05.
  - TREC-COVID chỉ có 50 topic, nên **luôn báo khoảng tin cậy 95%**.
- **So thứ hạng hệ thống (E3):** Kendall τ, kèm số cặp hệ thống bị đảo thứ tự.
- **Mô hình có huấn luyện (R1, R2):** báo cáo mean ± SD qua 3 seed.
- **Số công bố** lưu trong `src/eval/published.py`, mỗi số kèm nguồn, số bảng và dòng. Bảng và hình sinh tự động từ file này cùng `results/`.

---

## 9. Đo chi phí và tốc độ (E4)

### 9.1 Chỉ số

| Nhóm | Chỉ số |
|---|---|
| Tốc độ | Độ trễ mỗi truy vấn p50/p95/p99 (phía client, bỏ lệnh gọi khởi động); thông lượng với 1/4/16 luồng song song |
| Chi phí | Token vào/ra, **số request thật** (Jev tự chia nhóm khi vượt `split_state_budget`=26k); **USD/1.000 truy vấn**; với model local: số giây GPU và VRAM, quy ra USD theo giá thuê T4 (ghi rõ là ước lượng) |
| Độ tin cậy | Tỷ lệ lỗi, số lần bị 429, số lần retry; độ dao động điểm khi chạy lại cùng đầu vào |

### 9.2 Quy tắc đo
- Cùng máy, cùng khung giờ, trên **100 truy vấn cố định lấy từ NFCorpus test**. Chỉ tính các lệnh gọi **không trúng cache**.
- **Giá lấy từ trang chính thức vào ngày chạy**, lưu trong `configs/pricing.yaml` kèm ngày. **Không hardcode giá trong code.**
- GPT báo cáo 2 mức: gọi thời gian thực và Batch API.
- Token mỗi hãng tính theo tokenizer riêng, nên **chỉ so bằng USD và số request**.
- Đối chiếu chi phí tự tính với tổng tiền trên dashboard thanh toán sau mỗi ngày chạy.

**Ước lượng khối lượng R5:**
- E1: (50 + 323 + 300) truy vấn × 9 cửa sổ ≈ **6.060 lệnh gọi** cho mỗi cỡ GPT.
- E3(a): 279 × 9 ≈ **2.510 lệnh gọi**.
- Chạy `--dry-run` để ra USD trước khi chạy thật (mục 16).

### 9.3 Các vai trò được đo

| Vai trò | Phương án |
|---|---|
| Rerank | R1–R6 (R5 với 2 cỡ GPT) và 4 reranker local phụ |
| Cascade | Cross-encoder (R3 hoặc R4) lọc top-100 xuống top-20, rồi mới gọi Jev hoặc GPT |
| Sinh câu trả lời (demo) | GPT 2 cỡ, chỉ đo chi phí và độ trễ, không đo chất lượng |

**Thí nghiệm quy mô:** chi phí và độ trễ theo số ứng viên k = 10/20/50/100. Kỳ vọng có bước nhảy khi Jev phải chia nhóm.

### 9.4 Đầu ra
1. **Biểu đồ Pareto:** trục ngang USD/1.000 truy vấn (thang log), trục dọc nDCG@10, kích thước điểm là p95.
2. **Hiệu quả trên mỗi đô la:** mức tăng nDCG@10 so với R0 chia cho chi phí tăng thêm.
3. **Ngân sách độ trễ:** cấu hình nào dưới 1 giây hoặc dưới 3 giây mỗi truy vấn.
4. **Bảng quyết định:** dùng Jev, GPT hay model local. Quy tắc: giữ các phương án không kém phương án tốt nhất một cách có ý nghĩa thống kê, rồi chọn phương án rẻ nhất mà vẫn nằm trong ngân sách độ trễ.

### 9.5 Log của mỗi lệnh gọi (JSONL)
```python
@dataclass
class CallLog:
    run_id: str; role: str; model: str; mode: str
    query_id: str; n_candidates: int
    input_tokens: int; output_tokens: int; n_requests: int
    latency_ms: float; cost_usd: float
    cache_hit: bool; status: str; retries: int; ts: str
```
Với OpenAI, lấy số token từ trường `usage` trong response. Với Jev, kiểm tra `detail=True` có trả usage không. Nếu không, ước lượng bằng tokenizer hoặc `length_fn` của thư viện và ghi rõ là số ước lượng.

---

## 10. Mốc so sánh đã công bố

### 10.1 Mốc chính: Abdallah et al. 2025
[*How Good are LLM-based Rerankers? An Empirical Analysis of State-of-the-Art Reranking Models*](https://arxiv.org/abs/2508.16757), EMNLP Findings 2025.

- 22 phương pháp, 40 biến thể.
- BM25 (Pyserini) lấy top-100, rerank, đo nDCG@10.
- Chạy bằng toolkit Rankify với cài đặt mặc định. Một số dòng (RankGPT, monoT5-3B, Cohere) chép từ bài gốc.

Các dòng trích từ bảng 2–3 (nDCG@10, ×100; đã kiểm với PDF ngày 06/11/2026):

| Nhóm | Reranker | TREC-COVID | NFCorpus | SciFact |
|---|---|---:|---:|---:|
| — | BM25 | 59,47 | 30,75 | 67,89 |
| Cross-encoder | monoBERT (340M) | 70,01 | 36,88 | 71,36 |
| Cross-encoder | bge-reranker-base | 67,50 | 31,10 | 70,60 |
| Cross-encoder | bge-reranker-large | 74,30 | 34,80 | 74,10 |
| Cross-encoder | **bge-reranker-v2-m3** (mốc tái lập) | **74,79** | **33,84** | **73,48** |
| Cross-encoder | mxbai-rerank-base | 84,00 | 35,64 | 72,33 |
| Cross-encoder | Cohere Rerank-v2 | 81,81 | 36,36 | 74,44 |
| Seq2seq | MonoT5-base | 72,24 | 34,81 | 73,14 |
| Seq2seq | MonoT5-3B | 80,71 | 38,97 | 76,57 |
| Seq2seq | InRanker-3B | 81,75 | 38,25 | 78,31 |
| LLM listwise | RankGPT gpt-3.5-turbo | 76,67 | 35,62 | 70,43 |
| LLM listwise | RankGPT gpt-4¹ | 85,51 | 38,47 | 74,95 |
| LLM listwise | RankZephyr 7B | 80,70 | 36,58 | 75,13 |
| LLM listwise | ListT5-3B | 84,70 | 37,70 | 77,0 |
| LLM setwise | Setwise Flan-T5-XXL (bubblesort) | 76,8 | 34,6 | 75,4 |

¹ RankGPT dùng gpt-4 xếp lại top-30 do gpt-3.5 đã xếp, để giảm chi phí ([Sun et al. 2023](https://arxiv.org/abs/2304.09542), bảng 1).

### 10.2 Mốc phụ

| Nguồn | Nội dung | Dùng để |
|---|---|---|
| [RankGPT](https://arxiv.org/abs/2304.09542) | Thiết lập gốc: BM25 Pyserini top-100, cửa sổ 20, bước 10 | Cơ sở của R5 |
| [Pyserini 2CR BEIR](https://castorini.github.io/pyserini/2cr/beir.html) | BM25 flat nDCG@10: TREC-COVID 0,595, NFCorpus 0,322. BM25 multifield: 0,656 và 0,325. R@100 flat: 0,109 và 0,246 | Đối chiếu E0. SciFact: **TODO** lấy số trên trang 2CR |
| [MedCPT](https://arxiv.org/abs/2307.00589), bảng 1 | MedCPT (retriever + cross-encoder): 0,709 / 0,355 / 0,761 | **Chỉ tham khảo**, vì first-stage khác (MedCPT retriever) |
| [BEIR](https://arxiv.org/abs/2104.08663), bảng 4 | Hole@10 trên TREC-COVID: BM25 6,4%, docT5query 2,8%, ANCE 14,4%, TAS-B 31,8%, BM25+CE 1,6%. Sau khi chấm thêm 980 cặp: ANCE 0,654 → 0,735, ColBERT 0,677 → 0,735 | Giả thuyết cho E3 |
| [SciFact-Open](https://arxiv.org/abs/2210.13777) | 209 → 460 cặp bằng chứng sau khi gom pool từ 4 hệ thống; các hệ thống kiểm chứng claim giảm ít nhất 15 F1 khi chuyển sang kho 500K | Dữ liệu và bối cảnh cho E3 |
| [jev-reranker](https://huggingface.co/blog/hotchpotch/introducing-jev-reranker) (NanoHotpotQA) | hybrid 0,833 → `rerank` 0,969 | Kiểm tra cài đặt Jev ở giai đoạn 0 |

### 10.3 Cách so
- **Chỉ đặt cạnh bảng 10.1 sau khi E0 đạt.** Dòng của nhóm in đậm hoặc tô màu; dòng công bố giữ nguyên số và ghi nguồn.
- **NFCorpus:** BM25 trong bài báo là 30,75, nhưng Pyserini 2CR ghi 32,2 (flat).
  - Nếu E0 ra khoảng 32,2, vẫn dùng top-100 của nhóm cho mọi reranker.
  - Khi đặt cạnh bảng thì ghi chú độ lệch nền khoảng 1,4 điểm.
  - So sánh trên NFCorpus chủ yếu bằng **Δ so với BM25** thay vì số tuyệt đối.
- **Hình chính:** biểu đồ xếp hạng khoảng 45 dòng (40 dòng công bố cộng các dòng của nhóm) cho mỗi bộ, tô màu theo thế hệ.
- **Hình phụ:** "dòng thời gian phương pháp", trục ngang là năm ra đời, trục dọc là nDCG@10.
- Các tuyên bố về Jev từ Elastic, Qdrant, Supermemory và tác giả `jev-reranker` là tiếng Anh, miền tổng quát. Viết thành **"kiểm chứng trên miền y sinh"**.

---

## 11. Dàn ý tiểu luận và slide

### 11.1 Tiểu luận
1. **Tóm tắt.**
2. **Giới thiệu** (yêu cầu 1): LLM bịa trong y sinh → cần RAG → reranker quyết định ngữ cảnh đưa vào LLM. Có nhiều thế hệ reranker, nên câu hỏi là chọn cái nào và đánh giá có đáng tin không. Nêu RQ1–RQ4 và đóng góp.
3. **Công trình liên quan:** BEIR; RankGPT, Setwise, RankZephyr, ListT5; Abdallah 2025; MedCPT; ESIM; LambdaMART; Jev; pooling và nhãn thiếu (BEIR Hole@10, TREC-COVID, SciFact-Open).
4. **Ngữ liệu** (yêu cầu 2): mục 4.1–4.7.
5. **Phương pháp** (yêu cầu 3): mục 5, 6. Mô tả kỹ BiLSTM-ESIM.
6. **Thực nghiệm và kết quả:** E0–E4.
7. **So sánh với kết quả công bố** (yêu cầu 4): mục 10.
8. **Phân tích ca tốt / không tốt** (yêu cầu 5).
9. **Demo RAG:** ảnh chụp và 2–3 ví dụ.
10. **Kết luận, hạn chế, hướng phát triển.**
11. **Phụ lục:** prompt, siêu tham số, bảng chi phí, toàn bộ số công bố đã trích.

### 11.2 Slide (khoảng 18 slide)
1. Tiêu đề
2. RAG y sinh và vai trò của reranker
3. Sáu thế hệ reranker
4. RQ và đóng góp
5. Dữ liệu: 3 bộ BEIR y sinh và SciFact-Open
6. Phân tích ngữ liệu
7. Thiết lập chung: BM25 top-100, nhãn có sẵn, không chấm tay
8. BiLSTM-ESIM
9. E0: tái lập khớp bài báo
10. **Bảng chính và biểu đồ xếp hạng 45 dòng**
11. Metadata và narrative (RQ2)
12. Jev và GPT 2×2, thiên vị vị trí
13. **Nhãn thiếu: SciFact-Open (RQ3)**
14. **Pareto chi phí–chất lượng (RQ4)**
15. Ca tốt và ca không tốt
16. Demo RAG
17. Kết luận và hạn chế
18. Tài liệu tham khảo

---

## 12. Cấu trúc code

> Thư mục gốc: `~/Documents/NLP/DOAN/` (git repo, nhánh `main`). Lệnh chạy: `make help`. Hướng dẫn cho người dùng: `HUONG_DAN.md`.

```
DOAN/
├── NLP_PROJECT_PLAN.md · NLP_PROJECT_PLAN_v1.md · HUONG_DAN.md · Makefile
├── API.example.json · API.json      # key API (API.json gitignore)
├── requirements.txt · requirements-kaggle.txt
├── configs/        models.yaml (model ID) · pricing.yaml (giá + ngày, ngưỡng 5 USD)
├── data/           # không commit: raw/, processed/, indexes/scifact-open, kaggle_pack/, cache/*.sqlite
├── src/
│   ├── data/       beir_loader · trec_covid (topic + qrels theo vòng) · scifact_open · splits (chia tập + rò rỉ)
│   │               metadata (CORD-19 + PubMed efetch + ATM) · pack (gói Kaggle)
│   ├── retrieval/  bm25 (Pyserini prebuilt BEIR flat; index tự dựng cho SciFact-Open)
│   ├── rerank/     lambdamart (R1) · gpt_listwise (R5) · jev (R6) · candidates
│   ├── kaggle_tasks/ crossenc (R3, R4, X1–X4) · medcpt_feat · biowordvec_cut · bilstm (R2) · common
│   ├── eval/       ir_metrics · significance · rank_correlation · systems · published (số công bố + nguồn)
│   ├── demo/       rag_app (Gradio)
│   └── utils/      paths · secrets (API.json) · io · cache (SQLite) · cost_logger · cost_guard
├── scripts/        prepare_data · kaggle_job · kaggle_pipeline · run_experiment · run_api · check_api
│                   make_tables · make_figures · corpus_analysis
├── kaggle/kernels/<task>/   # kernel.py + kernel-metadata.json sinh tự động
├── results/        runs/<bộ>/<split>/<hệ thống>.trec · kaggle/<task>/ · e0…e4/*.json · data_report/ · api_logs/
├── report/         tables/*.md · figures/*.png · draft/ (nháp tiểu luận)
└── tests/          test_api_mock (client giả) · test_data_eval
```

---

## 13. Lộ trình và tiêu chí hoàn thành

Deadline: **TODO, người dùng cung cấp**.

### Giai đoạn 0 — Chuẩn bị
- [x] `git init`; `.venv`; `requirements.txt`; `API.json`; `configs/`; Pyserini + JRE 21.
- [x] `cache`, `cost_logger`, `cost_guard`, `pricing.yaml` (giá OpenAI lấy ngày 06/11/2026).
- [ ] Người dùng: điền `API.json`, đặt giới hạn chi tiêu; `make check-api`.
- [ ] Kiểm tra `jev-reranker` trên NanoHotpotQA (`scripts/check_api.py --jev-nano`). **Đạt khi** nDCG@10 xấp xỉ 0,969.

### Giai đoạn 1 — Dữ liệu và tái lập
- [x] Loader 3 bộ BEIR, topic NIST, SciFact-Open, chia dev, kiểm tra rò rỉ (loại 19 câu train gần trùng; `results/data_report/splits.json`).
- [x] BM25 top-100 cho 3 bộ + SciFact-Open. **E0 BM25:** TREC-COVID 59,47 và SciFact 67,89 khớp tuyệt đối; NFCorpus 32,18 (khớp Pyserini 2CR, lệch +1,43 so với bài báo — mục 10.3).
- [ ] R4 bge-reranker-v2-m3 trên Kaggle. **E0 hoàn thành** khi lệch ≤ 1 điểm.
- [x] Metadata TREC-COVID: 9.604 bài ứng viên; PMID 47,8%, MeSH 40,1%, tạp chí 86,1%, năm 100%.
- [x] Phân tích ngữ liệu (`scripts/corpus_analysis.py`, hình `report/figures/fig_data_*`).

### Giai đoạn 2 — Reranker local / GPU
- [x] R1 LambdaMART (3 seed; dev nDCG@10 ≈ 0,745) + bản CV 5-fold M0/M1 trên TREC-COVID.
- [ ] R3 MedCPT-CE, R4, 4 reranker phụ (Kaggle `crossenc`).
- [x] BioWordVec cắt theo vocab: phủ 94,7% (159.423/168.345 từ).
- [ ] R2 BiLSTM-ESIM, 3 seed (Kaggle `bilstm`). **Đạt khi** nDCG@10 trên dev cao hơn R0, hoặc đã phân tích lý do.
- [x] Metric, bootstrap + Holm, Kendall τ, Judged@10, `published.py`.

### Giai đoạn 3 — Reranker API (chờ key)
- [x] Code R5 (RankGPT, Responses API, structured outputs) và R6 (Jev); test bằng client giả; dry-run ước tính khoảng 41 USD (khoảng 19 USD nếu bỏ GPT-6.1 Sol).
- [ ] Chạy thật `make api-run CONFIRM=1` → **E1 hoàn thành**; E2 (2×2 tiêu chí, listwise/pointwise, thiên vị vị trí, biến thể truy vấn).

### Giai đoạn 4 — Nhãn thiếu, chi phí, demo
- [x] Index SciFact-Open 500K + BM25 top-100; code E3 (nhãn gốc / đã soát; TREC-COVID r = 1..4, condensed).
- [ ] E3 đầy đủ khi có run của mọi reranker.
- [x] Code E4 (độ trễ từ log Kaggle/API, USD/1.000 truy vấn, Pareto).
- [x] Demo RAG Gradio (`make demo`).
- [ ] Phân tích lỗi theo từng truy vấn (sau khi có đủ run).

### Giai đoạn 5 — Viết
- [x] Bảng và hình sinh tự động (`make report`).
- [ ] Tiểu luận (nháp trong `report/draft/`) và slide theo mục 11. Mọi con số truy được về file kết quả hoặc về bảng của bài báo.

---

## 14. Rủi ro và dự phòng

| Rủi ro | Dự phòng |
|---|---|
| E0 không khớp số bài báo | Kiểm tra trường truy vấn, tên index, cắt độ dài, fp16. Dùng top-100 có sẵn của Rankify nếu có. Báo cáo cả hai số; so bằng Δ so với BM25 |
| BM25 NFCorpus lệch (30,75 so với 32,2) | Xem mục 10.3 |
| Vượt chi phí API (R5 khoảng 6.000 lệnh gọi mỗi cỡ GPT) | Cache, Batch API, cost guard, `--dry-run`. `gpt_large` chạy trên tập con thì **phải ghi rõ** là không so trực tiếp với bảng |
| Nhiễm dữ liệu (các bộ công khai từ 2020–2022, GPT có thể đã thấy) | Ghi vào phần hạn chế. Tham khảo cách Abdallah 2025 dùng truy vấn mới (FutureQueryEval) để thảo luận |
| TREC-COVID chỉ có 50 topic | Báo khoảng tin cậy. Kết luận chính dựa thêm vào NFCorpus (323) và SciFact (300) |
| SciFact-Open vẫn còn bài chưa chấm (pool chỉ từ 4 hệ thống) | Báo Judged@10. **Không điền nhãn** bằng bất kỳ cách nào |
| Kho 500K tốn đĩa và thời gian | Chỉ index BM25. Đặc trưng MedCPT của R1 chỉ tính trên top-100 |
| API Jev đổi hoặc bị giới hạn tốc độ | Ghim phiên bản; retry có backoff; ghi lại ngày chạy |
| BiLSTM yếu | Đây là kết quả có ý nghĩa. Phân tích nguyên nhân: OOV, độ dài, thiếu tiền huấn luyện, zero-shot trên TREC-COVID |
| Giấy phép dữ liệu | Chỉ phát hành file run, ID và script |

---

## 15. Việc nhóm phải tự làm

**Đồ án không có bước chấm tay nào.** Claude không làm thay được, hoặc không nên làm thay, các việc sau:

1. **Tài khoản và key:** tạo API key OpenAI, TypeSafe (NCBI nếu cần); nạp tiền và đặt giới hạn chi tiêu.
2. **Duyệt và chịu trách nhiệm** nội dung tiểu luận, slide; tự thuyết trình và trả lời câu hỏi.
3. **Kiểm tra quy định của môn về việc dùng công cụ AI,** và ghi rõ trong tiểu luận nếu môn yêu cầu.
4. **Duyệt các lần chạy API** có chi phí ước tính vượt ngưỡng trong mục 16.
5. **Cung cấp deadline** và đồng ý `git init`.

---

## 16. Quy tắc làm việc cho Claude

- **Đầu mỗi phiên đọc file này.** Cuối phiên cập nhật checklist ở mục 13 và nhật ký ở mục 17.
- **Không chấm tay, không dùng LLM làm người chấm** ở bất kỳ thí nghiệm nào. GPT và Jev chỉ là hệ thống bị đánh giá.
- **E0 phải đạt trước khi đặt bất kỳ số nào của nhóm cạnh bảng công bố.**
- **Không chỉnh gì trên test.** Mọi ngưỡng, siêu tham số, prompt đều chọn trên dev.
- **Mọi lệnh gọi API** đi qua `cache` và `cost_logger`. Trước khi chạy một job có chi phí ước tính **trên 5 USD** (sửa trong `configs/`), chạy `--dry-run` để ước tính, **báo người dùng và chờ đồng ý**.
- **Ghim phiên bản:** khóa thư viện; model ID trong `configs/models.yaml`; ghi ngày chạy vào mỗi `results/<run_id>/config.yaml`.
- **Seed cố định** (0/1/2) cho mô hình có huấn luyện.
- **Không commit** dữ liệu thô, abstract, cache API hay key.
- **Báo cáo trung thực:** kết quả âm tính và thí nghiệm thất bại vẫn ghi lại. Không có con số nào trong tiểu luận mà không truy được về file kết quả hoặc về bảng của bài báo (`published.py`).
- Mục nào có **TODO: xác minh** thì phải kiểm tra lại trước khi dùng số liệu hoặc API tương ứng.

---

## 17. Nhật ký quyết định

| Ngày | Quyết định | Lý do |
|---|---|---|
| 2026-10-25 | Đề tài: RAG y tế, có thành phần LSTM | Theo yêu cầu của môn |
| 2026-10-26 | Bỏ ViHealthQA và PubMedQA, chọn BioASQ Task 13b | (v1) Nhiều bài đúng mỗi câu, có snippet và metadata MeSH |
| 2026-11-06 | (v1) Trọng tâm là dữ liệu nhóm tự xây (BioASQ-MetaRR) | Theo định hướng của người dùng lúc đó. **Đã thay**, xem các dòng dưới |
| 2026-11-06 | **Chỉ dùng GPT API**; Jev qua `jev-reranker` (hotchpotch, MIT) | Ràng buộc tài nguyên |
| 2026-11-06 | LSTM = **BiLSTM-ESIM reranker** | Yêu cầu của môn; đúng trọng tâm rerank |
| 2026-11-06 | **Chuyển sang v2. Bỏ BioASQ**, dùng TREC-COVID, NFCorpus, SciFact (BEIR) | Nhãn test của BioASQ 13b thiếu nên phải soát tay. Kho tự dựng từ PubMed không so trực tiếp được với kết quả công bố. Không cần đăng ký |
| 2026-11-06 | **Không chấm tay, không dùng LLM làm người chấm** | Yêu cầu của người dùng. Mọi nhãn lấy từ NIST, chuyên gia hoặc quy tắc tự động có sẵn |
| 2026-11-06 | Mốc so sánh chính: **Abdallah et al. 2025** (22 phương pháp, 40 biến thể) | Cùng thiết lập BM25 top-100. Nhóm chỉ chạy dòng chưa có, cộng 2 dòng tái lập |
| 2026-11-06 | Mọi reranker dùng chung **BM25 top-100** (thay cho top-50 của v1) | Khớp thiết lập bài báo. Jev tự chia nhóm khi vượt 26k, nên ghi số request thật |
| 2026-11-06 | Metadata câu hỏi dùng **trường của NIST** (`query`/`question`/`narrative`) thay vì GPT trích | Có sẵn, không cần kiểm tay. `narrative` dùng làm tiêu chí y khoa cho Jev/GPT |
| 2026-11-06 | RQ nhãn thiếu dùng **SciFact-Open** (`provenance` citation/pooling) và **qrels theo vòng của TREC-COVID** | Nhãn soát lại do chuyên gia/NIST làm sẵn, thay cho `qrels+` chấm tay của v1 |
| 2026-11-06 | **RAG chỉ là demo**, không đánh giá định lượng. Bỏ LLM-judge và ideal answer | Theo người dùng. Trọng tâm là reranker |
| 2026-11-06 | Bỏ dự phòng MultiHop-RAG | Không còn phụ thuộc vào việc đăng ký BioASQ |
| 2026-11-06 | GPU dùng **Kaggle** (Kaggle CLI), key API để trong **`API.json`**, môi trường `.venv` | Theo người dùng; máy không có GPU và không có `uv` |
| 2026-11-06 | R5: `gpt-6-luna` (toàn bộ top-100) + `gpt-6.1-sol` chỉ xếp lại top-30 | Rẻ; đối xứng với RankGPT gpt-3.5 + gpt-4 top-30. Không dùng `gpt-6-astra` (đắt gấp 5 lần) |
| 2026-11-06 | Jev chia nhóm bằng `length_fn` ước lượng | Tokenizer mặc định của `jev-reranker` là repo bị khóa trên HF |
| 2026-11-06 | E2/E3 trên TREC-COVID dùng CV 5-fold theo topic khi cần chọn tham số (λ MeSH, R1-M1) | TREC-COVID không có dev; không chỉnh trên topic đang chấm |
| 2026-11-06 | E3 thêm nDCG@10 condensed và đường cong theo vòng 1..4 | Kho vòng 1 nhỏ hơn kho BEIR nhiều, nên nhãn vòng 1 cho Judged@10 chỉ khoảng 9% |
| 2026-11-06 | Biến thể truy vấn ở E2 giữ cố định ứng viên (BM25 Q-q) và chỉ đổi văn bản đưa vào reranker | Tách riêng tác động lên reranker; BM25 với truy vấn đổi báo riêng |

---

## 18. Tài liệu tham khảo

- **Mốc so sánh chính:** Abdallah et al. 2025, *How Good are LLM-based Rerankers?*: https://arxiv.org/abs/2508.16757
- Rankify: https://arxiv.org/abs/2502.02464
- RankGPT (Sun et al., EMNLP 2023): https://arxiv.org/abs/2304.09542
- Setwise (Zhuang et al., SIGIR 2024): https://arxiv.org/abs/2310.09497
- BEIR: https://arxiv.org/abs/2104.08663
- Pyserini BEIR reproductions (2CR): https://castorini.github.io/pyserini/2cr/beir.html
- MedCPT: https://arxiv.org/abs/2307.00589
- ESIM (Chen et al., ACL 2017): https://arxiv.org/abs/1609.06038
- TREC-COVID: overview https://arxiv.org/abs/2104.09632 · dữ liệu và qrels theo vòng https://ir.nist.gov/trec-covid/data.html
- NFCorpus: https://www.cl.uni-heidelberg.de/statnlpgroup/nfcorpus/
- SciFact: https://github.com/allenai/scifact
- SciFact-Open: https://arxiv.org/abs/2210.13777 · https://github.com/dwadden/scifact-open
- jev-reranker: https://huggingface.co/blog/hotchpotch/introducing-jev-reranker · https://github.com/hotchpotch/jev-reranker
- Các bài về Jev:
  - Elastic: https://www.elastic.co/search-labs/blog/ecommerce-search-reranking-llm-alternative-jev
  - Qdrant: https://qdrant.tech/blog/jevjitsu/
  - Supermemory: https://supermemory.ai/blog/jev-memory-context-engineering/
  - Hindsight: https://hindsight.vectorize.io/blog/2026/09/24/adding-jev-reranker-what-we-learned
