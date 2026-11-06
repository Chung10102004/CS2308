# BioASQ-MetaRR — Kế hoạch đồ án NLP

> ⚠️ **Bản cũ (v1), đã được thay bằng `NLP_PROJECT_PLAN.md` (v2) ngày 06/11/2026.** Chỉ giữ để tham khảo, không làm theo file này.

> Đồ án cuối kỳ môn **Chuyên đề nghiên cứu xử lý ngôn ngữ tự nhiên**.
> Đề tài khung: *RAG trên domain nhỏ, QA*. Dùng chung một đề tài cho **thuyết trình** và **tiểu luận**.
> Người thực hiện code: Claude (toàn bộ). Các việc chỉ con người làm được nằm ở [mục 15](#15-việc-nhóm-phải-tự-làm).
> Trạng thái: **kế hoạch, chưa có code**. Cập nhật lần cuối: 06/11/2026.

---

## 0. Tóm tắt

Nhóm xây dựng **BioASQ-MetaRR**, một bộ dữ liệu rerank y sinh dựng trên BioASQ Task 13b. Bộ dữ liệu gồm:

- kho ứng viên cố định cho mỗi câu hỏi, lấy từ PubMed;
- metadata cho tài liệu (MeSH, loại bài, năm, tạp chí);
- metadata cho câu hỏi (do GPT trích xuất, có kiểm tra tay);
- tập nhãn đã soát lại (`qrels+`).

Trên bộ dữ liệu này, nhóm dựng một pipeline RAG và so sánh **sáu thế hệ reranker**: LambdaMART, BiLSTM-ESIM, MedCPT cross-encoder, bge-reranker, GPT listwise và Jev (TypeSafe). Các reranker được so theo bốn trục: chất lượng truy xuất, chất lượng câu trả lời, **chi phí** và **tốc độ**.

Pipeline RAG chỉ là hạ tầng. Trọng tâm của đồ án là **dữ liệu nhóm tự xây** và **các phân tích dựa trên nó**.

---

## 1. Yêu cầu của môn

| # | Yêu cầu | Đáp ứng ở |
|---|---|---|
| 1 | Giới thiệu bài toán | Mục 2, mục 11 |
| 2 | Phân tích ngữ liệu | Mục 4.8 (phần nặng nhất, vì là phần nhóm tự làm) |
| 3 | Phương pháp tiếp cận (**ít nhất LSTM**) | Mục 5, 6. LSTM là **BiLSTM-ESIM reranker** (R2) |
| 4 | So sánh kết quả công bố gần đây | Mục 10 |
| 5 | Giải thích trường hợp mô hình tốt / không tốt | Mục 7 (phân tích), mục 11 |

---

## 2. Ý tưởng và đóng góp

### 2.1 Ý tưởng trong một câu
Dựng một bộ dữ liệu rerank y sinh giàu metadata, rồi dùng nó để đo xem **metadata**, **các thế hệ reranker**, **chất lượng nhãn** và **chi phí / tốc độ** ảnh hưởng thế nào đến một hệ thống RAG.

### 2.2 Hạ tầng và đóng góp

| | Nội dung | Cách làm |
|---|---|---|
| **Hạ tầng** (phải có, không phải đóng góp) | Pipeline RAG: first-stage, gọi reranker, GPT sinh đáp án, tính metric | Dùng công cụ có sẵn: `bm25s`, MedCPT, FAISS, OpenAI SDK, `jev-reranker` |
| **C1. Dữ liệu** ⭐ | Kho ứng viên, metadata tài liệu, metadata câu hỏi, `qrels+` | **Nhóm tự xây** |
| **C2. So sánh** | 6 thế hệ reranker × 3 mức metadata × 2 kiểu tiêu chí | Chạy trên dữ liệu của C1 |
| **C3. Phân tích** | Theo loại câu hỏi và MeSH; tách lỗi theo khâu; ảnh hưởng của nhãn thiếu; chi phí–tốc độ | Dựa trên kết quả C2 |

### 2.3 Câu hỏi nghiên cứu
- **RQ1 — Metadata:** metadata tài liệu (MeSH, loại bài) và metadata câu hỏi giúp reranker thế hệ nào, giúp bao nhiêu?
- **RQ2 — Thế hệ reranker:** LambdaMART → BiLSTM → cross-encoder → GPT / Jev xếp hạng ra sao trên dữ liệu y sinh?
- **RQ3 — Chất lượng nhãn:** nhãn của BioASQ được gom từ kết quả dự thi (pooling) nên bị thiếu. Sau khi soát lại, thứ hạng giữa các hệ thống có đổi không?
- **RQ4 — Tác động lên RAG:** rerank và lọc ngữ cảnh tốt hơn thì đáp án factoid và list tốt hơn bao nhiêu?
- **RQ5 — Chi phí và tốc độ:** ở mỗi vai trò (rerank, lọc, phân loại metadata, soát nhãn), nên dùng Jev, GPT hay mô hình local?

### 2.4 Câu đóng góp (dùng cho tiểu luận và slide)
> *"Chúng tôi xây dựng BioASQ-MetaRR, một bộ dữ liệu rerank y sinh gồm kho ứng viên cố định, metadata cho tài liệu và câu hỏi, và tập nhãn đã được soát lại. Trên bộ dữ liệu này, chúng tôi đánh giá sáu thế hệ reranker trong một pipeline RAG theo bốn trục: chất lượng truy xuất, chất lượng câu trả lời, chi phí và tốc độ. Chúng tôi chỉ ra metadata giúp reranker thế hệ nào, việc soát nhãn làm thay đổi kết luận so sánh ra sao, và ở vai trò nào một mô hình quyết định chuyên dụng (Jev) đáng dùng hơn LLM tổng quát."*

---

## 3. Ràng buộc và tài nguyên

| Loại | Chi tiết |
|---|---|
| LLM API | **Chỉ có OpenAI GPT.** Dùng cho: trích metadata câu hỏi, rerank listwise, sinh đáp án, LLM-judge |
| Jev | TypeSafe Jev, gọi qua thư viện [`jev-reranker`](https://github.com/hotchpotch/jev-reranker) (MIT, cần API key TypeSafe) |
| PubMed | NCBI E-utilities (`esearch`, `efetch`). Có API key thì gọi được 10 request/giây |
| Compute | CPU local; GPU Colab T4 cho MedCPT, bge-reranker, BiLSTM |
| Python | **3.11 trở lên** (`jev-reranker` yêu cầu). Quản lý môi trường bằng `uv` |
| Biến môi trường | `OPENAI_API_KEY`, `TYPESAFE_API_KEY`, `NCBI_API_KEY`, `NCBI_EMAIL` (lưu trong `.env`, không commit) |
| Ngân sách | Đặt giới hạn chi tiêu trên dashboard của OpenAI và TypeSafe. Code có chặn chi phí (xem mục 16) |

---

## 4. Dữ liệu

### 4.1 BioASQ Task 13b (2025)
Nguồn: [Overview of BioASQ Tasks 13b and Synergy13](https://ceur-ws.org/Vol-4038/paper_1.pdf), bảng 1.

| Tập | Số câu | Yes/No | List | Factoid | Summary | Tài liệu đúng TB/câu | Snippet đúng TB/câu |
|---|---:|---:|---:|---:|---:|---:|---:|
| Train | 5.389 | 1.459 | 1.047 | 1.600 | 1.283 | 9,74 | 12,78 |
| Test 1 | 85 | 17 | 23 | 26 | 19 | 2,68 | 3,74 |
| Test 2 | 85 | 17 | 19 | 27 | 22 | 2,71 | 3,06 |
| Test 3 | 85 | 22 | 22 | 20 | 21 | 3,00 | 3,66 |
| Test 4 | 85 | 26 | 19 | 22 | 18 | 3,15 | 3,92 |

- **Các trường JSON:** `id`, `body` (câu hỏi), `type`, `documents` (URL PubMed, trích ra PMID), `snippets` (`document`, `text`, offset), `exact_answer`, `ideal_answer`.
- **Cách lấy:** nhóm đăng ký tài khoản tại `participants-area.bioasq.org`, rồi tải tập train 13b và file đáp án (golden) của 4 batch test 13b.
- Số tài liệu đúng trên mỗi câu ở tập test thấp hơn hẳn tập train, vì nhãn test là sơ bộ, chưa được chuyên gia chấm lại. Đây là lý do cần làm C1-④.

### 4.2 Chia tập
- **test:** 4 batch 13b, tổng **340 câu**. Chỉ dùng để báo cáo kết quả cuối, **không bao giờ dùng để chỉnh tham số**.
- **dev:** **300 câu** tách ra từ tập train. Lấy từ các năm gần nhất và chia tầng theo loại câu hỏi. Dùng để chọn ngưỡng, siêu tham số và prompt.
- **train:** phần còn lại của tập train.
- **Quy tắc chống rò rỉ:**
  - Nếu dùng tập train mới hơn (14b), **phải loại mọi câu trùng `id` với test 13b**.
  - Kiểm tra câu gần trùng giữa train và test: TF-IDF cosine > 0,9 thì loại câu đó khỏi train. Ghi lại số câu đã loại.

### 4.3 C1-① Dựng kho ứng viên
1. **Truy vấn PubMed** bằng `esearch` với `sort=relevance` (Best Match) và `datetype=pdat`. Đặt `maxdate` bằng ngày phát hành batch, **TODO: xác minh ngày của từng batch 13b** trên trang BioASQ. Lấy `retmax=100` cho câu train, `retmax=200` cho câu test.
   - Câu hỏi dạng ngôn ngữ tự nhiên có thể không ra kết quả. Cách tạo truy vấn:
     - q1 = các từ khóa nối bằng AND (bỏ stopword và từ để hỏi);
     - nếu ít hơn N kết quả thì dùng q2 = các từ khóa nối bằng OR;
     - ghi lại câu nào đã dùng q2.
   - Nếu tỷ lệ phủ vẫn thấp, phương án dự phòng là cho GPT sinh truy vấn từ khóa. Khi đó phải ghi rõ là có LLM ở bước first-stage.
2. **Kho tài liệu** = hợp các kết quả `esearch` của mọi câu, cộng thêm **bài đúng của tập train**. **Không chèn bài đúng của tập test.**
3. **First-stage local** chạy trên kho này:
   - BM25 (`bm25s`, thử các biến thể: lowercase, bỏ stopword, stemming);
   - MedCPT dense (`ncbi/MedCPT-Query-Encoder`, `ncbi/MedCPT-Article-Encoder`, FAISS inner product);
   - hợp nhất bằng RRF (k=60) thành **top-100 cố định** cho mỗi câu.
4. **Đầu vào chung của mọi reranker là top-50.** Các reranker local chạy thêm bản top-100 để xem số ứng viên ảnh hưởng thế nào.
5. **Chất lượng kho** đo bằng Recall@50/100/200 trên tập test, tách theo từng nguồn (thí nghiệm E1). Đây là cận trên mà reranker có thể đạt.

Ước lượng: khoảng 5.700 câu × 100–200 bài, sau khi bỏ trùng có thể còn vài trăm nghìn abstract. Kiểm tra quy mô thật sau bước 1, nếu quá lớn thì giảm `retmax` cho tập train.

### 4.4 C1-② Metadata tài liệu
Gọi `efetch` (`db=pubmed`, `retmode=xml`, 200 PMID mỗi request), parse ra:

```json
{
  "pmid": "12345678",
  "title": "...",
  "abstract": "...",
  "abstract_sections": [{"label": "RESULTS", "text": "..."}],
  "journal": "...",
  "year": 2021,
  "pub_types": ["Randomized Controlled Trial", "Journal Article"],
  "mesh": [{"descriptor": "Breast Neoplasms", "ui": "D001943", "major": true, "qualifiers": ["drug therapy"]}],
  "keywords": ["..."],
  "chemicals": ["..."]
}
```

Lưu thành `corpus.jsonl`. Bài không có abstract thì giữ lại tiêu đề và đánh cờ `no_abstract`.

### 4.5 C1-③ Metadata câu hỏi
- Dùng GPT với **structured outputs** (JSON schema), chạy qua **Batch API**.
- Schema:

```json
{
  "entities": [{"text": "trastuzumab", "type": "drug"}],
  "mesh_candidates": ["Trastuzumab", "Breast Neoplasms"],
  "evidence_type_pref": "any | rct | systematic_review | cohort | case_report | guideline",
  "population": "string | null",
  "temporal_constraint": {"min_year": null, "max_year": null}
}
```

- **Kiểm tra `mesh_candidates` với từ điển MeSH chuẩn** (`esearch db=mesh`). Chỉ giữ những descriptor có UI hợp lệ, và ghi lại tỷ lệ bị loại.
- **Nhóm chấm tay 100 câu**, đo precision và recall của các trường. Xem mục 15.
- Các trường dạng nhãn cố định (`evidence_type_pref`, `population`) chạy thêm bằng Jev Choice để so chi phí và độ chính xác trong E6.

### 4.6 C1-④ Soát nhãn → `qrels+`
1. Ứng viên cần soát: các bài **không có nhãn đúng** nhưng được **ít nhất 2 reranker mạnh** đưa vào top-10, trên tập test.
2. **Jev (binary) và GPT (binary)** cùng đánh giá. Ca nào cả hai cùng nói "liên quan" thì đánh dấu là nghi bị thiếu nhãn.
3. **Nhóm xác nhận bằng tay:** ít nhất 100 ca, hoặc toàn bộ nếu đủ thời gian, theo bản hướng dẫn chấm ngắn. Claude chuẩn bị file chấm (CSV hoặc HTML).
4. `qrels+` = `qrels` gốc cộng các ca đã được người xác nhận. **Ghi rõ hạn chế:** người chấm không phải chuyên gia y sinh.

### 4.7 C1-⑤ Đóng gói
```
bioasq-metarr/
├── queries.jsonl          # id, type, query_metadata (không kèm nguyên văn nếu giấy phép cấm)
├── corpus_ids.jsonl       # PMID + metadata (MeSH, loại bài, năm, tạp chí)
├── candidates.trec        # top-100 mỗi câu (định dạng TREC run)
├── qrels.trec, qrels_plus.trec
├── scripts/rebuild.py     # tải lại abstract từ PubMed theo PMID
└── DATASHEET.md           # theo khung "Datasheets for Datasets"
```

**Bản quyền:** BEIR có ghi rằng dữ liệu BioASQ thuộc diện có bản quyền, và abstract PubMed thuộc nhà xuất bản. Vì vậy chỉ phát hành **PMID, metadata, nhãn và script dựng lại**, không phát hành nguyên văn câu hỏi và abstract nếu giấy phép không cho phép. **TODO:** đọc giấy phép của BioASQ trước khi phát hành.

### 4.8 Phân tích ngữ liệu (mục 2 của tiểu luận)
- Phân bố 4 loại câu hỏi; độ dài câu hỏi; số bài và số snippet đúng trên mỗi câu, so giữa train và test.
- Phân bố MeSH: top các nhánh của cây MeSH (C = bệnh, D = hóa chất/thuốc, G = hiện tượng…), loại bài, năm xuất bản.
- Độ dài abstract; tỷ lệ abstract có cấu trúc (có nhãn mục); tỷ lệ bài không có abstract.
- Độ trùng từ giữa câu hỏi và bài đúng, so với bài sai trong top-50. Chỉ số này giải thích vì sao BM25 mạnh hoặc yếu.
- Chất lượng kho: Recall@k theo từng nguồn và theo loại câu hỏi; số câu phải dùng truy vấn q2.
- Chất lượng metadata câu hỏi: precision và recall so với nhãn tay; tỷ lệ MeSH bị loại.
- Tỷ lệ nghi thiếu nhãn và tỷ lệ được người xác nhận.

---

## 5. Pipeline RAG (hạ tầng)

```
Câu hỏi ──► metadata câu hỏi (GPT, C1-③)
   │
   ▼
First-stage: BM25 + MedCPT → RRF → top-100 (cố định, từ C1-①) → top-50
   │
   ▼
RERANKER (R0–R6) × metadata (M0/M1/M2) ──► top-10 (BioASQ chấm tối đa 10 bài)
   │
   ▼
Chọn ngữ cảnh:  top-5 cố định   hoặc   Jev relevance_rerank (ngưỡng dò trên dev)
   │                                     └─ không bài nào vượt ngưỡng → từ chối (bản có cổng)
   ▼
GPT sinh đáp án (JSON theo loại câu hỏi) + trích dẫn PMID
```

**Định dạng đáp án GPT** (structured outputs):
- yes/no: `"yes"` hoặc `"no"`.
- factoid: tối đa 5 thực thể, xếp hạng.
- list: danh sách thực thể.
- summary/ideal: tối đa 200 từ, có trích dẫn `[PMID]`.

---

## 6. Mô hình

### 6.1 Các reranker

| ID | Thế hệ | Reranker | Cấu hình chính |
|---|---|---|---|
| R0 | — | Không rerank (giữ thứ tự RRF) | Baseline |
| R1 | Truyền thống | **LambdaMART** (LightGBM `LGBMRanker`, `lambdarank`) | Đặc trưng: BM25, TF-IDF cosine, MedCPT cosine, độ trùng MeSH câu hỏi–bài, khớp loại bài, năm, độ dài, có abstract hay không. Huấn luyện trên kho ứng viên của train, chỉnh trên dev |
| R2 | **LSTM** | **BiLSTM-ESIM** (PyTorch) | Embedding BioWordVec 200 chiều (file lớn, tải một lần rồi cắt theo vocab của kho). BiLSTM mã hóa 1 lớp, 200 chiều mỗi hướng → soft alignment → BiLSTM tổng hợp → avg+max pool → MLP → điểm. Đầu vào: câu hỏi + tiêu đề + abstract, cắt còn 256 token. Loss softmax listwise với 1 bài đúng và 7 bài sai lấy từ top-50 BM25. Adam, early stopping theo MAP trên dev. Seed 0/1/2 |
| R3 | Cross-encoder y sinh | `ncbi/MedCPT-Cross-Encoder` | Zero-shot |
| R4 | Cross-encoder tổng quát | `BAAI/bge-reranker-v2-m3` | Zero-shot |
| R5 | LLM | **GPT listwise** (kiểu RankGPT) | Cửa sổ 20, bước trượt 10, chạy trên top-50 (4 lệnh gọi). Kết quả là hoán vị PMID dạng JSON; PMID bị thiếu hoặc trùng thì nối vào cuối. Temperature 0 nếu model hỗ trợ |
| R6 | Mô hình quyết định | **Jev** qua `jev-reranker` | Chế độ listwise (mặc định) và pointwise; `threshold=0` khi rerank. Ghim phiên bản thư viện và tên model (mặc định là `jev-latest`, phải ghi lại) |

Model ID của GPT để trong `configs/models.yaml` (`gpt_small`, `gpt_large`). **Điền model ID hiện hành khi bắt đầu**, lấy từ trang models của OpenAI.

### 6.2 Các mức metadata
- **M0:** chỉ dùng văn bản.
- **M1:** thêm metadata tài liệu.
  - Reranker văn bản (R2–R6): chèn dòng `[MeSH: …] [Type: …] [Year: …]` vào trước abstract.
  - R1: metadata đã nằm sẵn trong đặc trưng.
- **M2:** M1 cộng thêm metadata câu hỏi: độ trùng MeSH câu hỏi–bài, khớp loại bằng chứng, ràng buộc thời gian.
  - R5, R6: đưa metadata câu hỏi vào ngữ cảnh của prompt hoặc instruction.
- **Boost hậu kỳ,** áp dụng đồng đều cho mọi reranker để so công bằng: `score' = score + λ · overlap_MeSH`, với λ dò trên dev.

### 6.3 Tiêu chí: chung chung và y khoa (cho thí nghiệm 2×2 ở E3)
Dùng cùng một nội dung tiêu chí cho cả Jev (`instruction`) lẫn GPT (prompt). **Định dạng `instruction` của Jev phải xác minh theo README:** một dict gồm `instructions` và `criteria` với các nhánh `true`/`false`.

- **Tiêu chí chung (generic):**
  - instructions: *"Judge whether the passage is relevant to the query."*
  - true: *"The passage is relevant to the query."*
  - false: *"The passage is not relevant to the query."*
- **Tiêu chí y khoa (medical):**
  - instructions: *"You are screening PubMed abstracts for a biomedical question-answering system. Judge whether the abstract provides evidence that helps answer the question."*
  - true: *"The abstract addresses the same entities as the question (disease, gene, drug, intervention, population) and reports findings, definitions or facts that help answer it."*
  - false: *"The abstract is off-topic, only shares background terms, concerns a different entity or population, or contains nothing that helps answer the question."*

---

## 7. Thí nghiệm

| # | Thí nghiệm | Cấu hình | Metric | RQ |
|---|---|---|---|---|
| **E1** | Chất lượng kho ứng viên | PubMed / BM25 (các biến thể) / MedCPT / RRF | Recall@50/100/200, theo từng loại câu hỏi | C1 |
| **E2** | **Bảng chính** | R0–R6 × M0/M1/M2. R5 và R6 chỉ dùng tiêu chí chung | MAP (theo cách chấm chính thức), nDCG@10, P@10, MRR | RQ1, RQ2 |
| **E3** | Jev và GPT | 2×2 (R5, R6) × {tiêu chí chung, tiêu chí y khoa} ở M0. Thêm Jev listwise so với pointwise. **Thiên vị vị trí:** xáo thứ tự ứng viên 3 lần trên 100 câu, đo Kendall tau | Như E2, cộng độ ổn định | RQ2 |
| **E4** | Soát nhãn | Chấm lại mọi cấu hình E2 bằng `qrels+` | Độ chênh metric; Kendall tau giữa thứ hạng hệ thống trước và sau | RQ3 |
| **E5** | RAG trọn vẹn | closed-book / RAG top-5 với {R0, R3 hoặc reranker local tốt nhất, R5, R6} / lọc động bằng Jev / lọc bằng Jev + cổng từ chối / oracle (bài và snippet đúng) | yes/no macro-F1, factoid MRR (strict/lenient), list F1, ideal ROUGE-2/SU4 + judge; số token ngữ cảnh; đường cong risk–coverage cho bản có cổng | RQ4 |
| **E6** | Chi phí và tốc độ | Mọi vai trò dùng API hoặc mô hình (xem mục 9) | USD/1.000 câu, p50/p95/p99, thông lượng, tỷ lệ lỗi | RQ5 |

**Phân tích (cho mục 5 của tiểu luận):**
- Theo loại câu hỏi. Lưu ý yes/no đã gần bão hòa (Phase A+ của 13b đạt 0,87–1,0), nên **tập trung vào factoid và list**.
- Theo nhánh MeSH và loại bài.
- Tách lỗi theo khâu: first-stage bỏ sót, reranker xếp sai, hay generator sai (so với oracle).
- Feature importance của LambdaMART.
- Các ca Jev và GPT bất đồng; các ca metadata giúp và metadata hại.
- Các ca "sai" hóa ra đúng sau khi soát nhãn.
- Chọn 3–5 ví dụ cụ thể cho mỗi nhóm.

---

## 8. Đánh giá

- **Truy xuất:**
  - Dùng code chấm chính thức của BioASQ (TODO: xác minh repo `BioASQ/Evaluation-Measures`) để có MAP top-10 khớp với bảng kết quả cuộc thi.
  - Dùng thêm `ir_measures` hoặc `pytrec_eval` cho nDCG@10, MAP@10, Recall@k, MRR.
- **Đáp án:** metric chính thức của BioASQ: macro-F1 cho yes/no; strict/lenient accuracy và MRR cho factoid; P/R/F1 cho list; ROUGE-2 và ROUGE-SU4 cho ideal answer.
- **Kiểm định ý nghĩa thống kê:**
  - Paired bootstrap (10.000 lần lấy mẫu) hoặc randomization test trên điểm từng câu.
  - Hiệu chỉnh Holm khi so nhiều hệ thống với một baseline.
  - Đánh dấu * khi p < 0,05.
- **LLM-judge:**
  - Chỉ dùng cho ideal answer.
  - **Model chấm ≠ model sinh** (khác cỡ GPT).
  - Kiểm chứng bằng chấm tay 50–100 câu (Spearman). Ghi vào phần hạn chế rằng judge và generator cùng hãng.
- **Mô hình có huấn luyện (R1, R2):** báo cáo mean ± SD qua 3 seed.

---

## 9. Đo chi phí và tốc độ (E6)

### 9.1 Chỉ số

| Nhóm | Chỉ số |
|---|---|
| Tốc độ | Độ trễ mỗi câu p50/p95/p99 (phía client, bỏ lệnh gọi khởi động); thông lượng với 1/4/16 luồng song song |
| Chi phí | Token vào/ra, **số request thật** (Jev tự chia nhóm khi vượt `split_state_budget`=26k); **USD/1.000 câu**; với model local: số giây GPU và VRAM, quy ra USD theo giá thuê T4 (ghi rõ là ước lượng) |
| Độ tin cậy | Tỷ lệ lỗi, số lần bị 429, số lần retry; độ dao động điểm khi chạy lại cùng đầu vào |

### 9.2 Quy tắc đo
- Cùng máy, cùng khung giờ, trên **100 câu test cố định**. Chỉ tính các lệnh gọi **không trúng cache**.
- **Giá lấy từ trang chính thức vào ngày chạy**, lưu trong `configs/pricing.yaml` kèm ngày. **Không hardcode giá trong code.**
- GPT báo cáo 2 mức: gọi thời gian thực và Batch API (dùng cho các việc offline như metadata, soát nhãn, chấm điểm).
- Token mỗi hãng tính theo tokenizer riêng, nên **chỉ so bằng USD và số request**.
- Đối chiếu chi phí tự tính với tổng tiền trên dashboard thanh toán sau mỗi ngày chạy.

### 9.3 Các vai trò được đo

| Vai trò | Phương án |
|---|---|
| Rerank | R1–R6 (R5 với 2 cỡ GPT) |
| Lọc ngữ cảnh / cổng | Jev `relevance_rerank` · GPT binary · ngưỡng QPP |
| Phân loại metadata câu hỏi (nhãn cố định) | GPT structured · Jev Choice |
| Soát nhãn | Jev binary · GPT binary |
| Sinh đáp án | GPT 2 cỡ. Đo phần token tiết kiệm được nhờ lọc ngữ cảnh |

**Thí nghiệm quy mô:**
- Chi phí và độ trễ theo số ứng viên k = 10/20/50/100. Kỳ vọng có bước nhảy khi Jev phải chia nhóm.
- **Cascade:** cross-encoder lọc top-50 xuống top-10, rồi mới gọi Jev hoặc GPT.

### 9.4 Đầu ra
1. **Biểu đồ Pareto:** trục ngang USD/1.000 câu (thang log), trục dọc nDCG@10, kích thước điểm là p95.
2. **Hiệu quả trên mỗi đô la:** mức tăng MAP so với R0 chia cho chi phí tăng thêm.
3. **Ngân sách độ trễ:** cấu hình nào dưới 1 giây hoặc dưới 3 giây mỗi câu.
4. **Chi phí cả pipeline:** rerank + lọc + sinh đáp án.
5. **Bảng quyết định:** "dùng Jev hay GPT hay model local ở vai trò nào". Quy tắc: giữ các phương án không kém phương án tốt nhất một cách có ý nghĩa thống kê, rồi chọn phương án rẻ nhất mà vẫn nằm trong ngân sách độ trễ.

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
Với OpenAI, lấy số token từ trường `usage` trong response. Với Jev, kiểm tra `detail=True` có trả usage không; nếu không thì ước lượng bằng tokenizer hoặc `length_fn` của thư viện, và ghi rõ là số ước lượng.

---

## 10. Mốc so sánh đã công bố

| Nguồn | Thiết lập | Số liệu |
|---|---|---|
| [BEIR](https://arxiv.org/pdf/2104.08663) (BioASQ 8b, 14,9 triệu bài, 500 câu, 4,7 bài đúng/câu) | nDCG@10 | BM25 **0,465** · DeepCT 0,407 · SPARTA 0,351 · docT5query 0,431 · DPR 0,127 · ANCE 0,306 · TAS-B 0,383 · GenQ 0,398 · ColBERT 0,474 · **BM25+CE 0,523** |
| [BioASQ 13b](https://ceur-ws.org/Vol-4038/paper_1.pdf), Phase A, batch 1 (sơ bộ) | MAP tài liệu | Tốt nhất 0,4246 (`bioinfo-4`) · hệ thống tên "Baseline top 20" 0,3806 · "Using LLM alone" 0,3622 · `GPT4O` 0,0665 |
| BioASQ 13b, Phase A+ (RAG), batch 2 | Đáp án | yes/no F1 tốt nhất 1,0 (phần lớn 0,87–0,94) · factoid MRR tốt nhất 0,5926 · list F1 tốt nhất 0,3880 |
| BioASQ 13b, Phase B (oracle), batch 2 | Đáp án | factoid MRR tốt nhất 0,7037 · list F1 tốt nhất 0,6152 · `BioASQ_Baseline`: yes/no 0,4632, MRR 0,2772, list F1 0,2528 |
| [MIRAGE / MedRAG 2024](https://arxiv.org/pdf/2402.13178) | BioASQ-Y/N accuracy | GPT-4: CoT 84,3 → MedRAG 92,56 · GPT-3.5: CoT 74,27 → MedRAG 90,29 (**TODO: đối chiếu bảng gốc**) |
| [jev-reranker](https://huggingface.co/blog/hotchpotch/introducing-jev-reranker) (NanoHotpotQA, 50 câu, 100 ứng viên) | nDCG@10 | hybrid 0,833 → `rerank` 0,969 → `relevance_rerank`@0,2 0,975 (giữ trung bình 7,62 bài, loại 92,38%, giữ đủ 97/97 bài đúng). Tác giả viết "tương đương bge-reranker-v2-m3" nhưng không đưa số |
| [RankGPT](https://arxiv.org/abs/2304.09542) (Sun et al., EMNLP 2023) | Phương pháp | Cơ sở cho R5 |

**Cách so:**
- Số của BioASQ được tính trên **toàn bộ PubMed**, còn nhóm tìm trên **kho con**. Vì vậy chỉ so xu hướng và khoảng cách, không tuyên bố vượt.
- Mục tiêu chính là tái lập được khoảng tăng tương tự BM25 → BM25+CE (khoảng +5,8 nDCG@10), rồi xem GPT, Jev và metadata có vượt mức đó không.
- Các tuyên bố về Jev từ Elastic, Qdrant, Supermemory và tác giả `jev-reranker` là tiếng Anh, miền tổng quát. Viết thành **"kiểm chứng trên miền y sinh"**.

---

## 11. Dàn ý tiểu luận và slide

### 11.1 Tiểu luận
1. **Tóm tắt.**
2. **Giới thiệu** (yêu cầu 1): LLM bịa trong y sinh → cần RAG → truy xuất là nút thắt, bằng chứng là khoảng cách giữa Phase A+ và Phase B của BioASQ (0,1–0,2 điểm với factoid và list). Nêu RQ1–RQ5 và đóng góp.
3. **Công trình liên quan:** BioASQ, BEIR, MedCPT, RankGPT, MIRAGE, Multi-Meta-RAG, Jev.
4. **Ngữ liệu và xây dựng dữ liệu** (yêu cầu 2): mục 4.
5. **Phương pháp** (yêu cầu 3): mục 5, 6. Mô tả kỹ BiLSTM-ESIM.
6. **Thực nghiệm và kết quả:** E1–E6.
7. **So sánh với kết quả công bố** (yêu cầu 4): mục 10.
8. **Phân tích ca tốt / không tốt** (yêu cầu 5).
9. **Kết luận, hạn chế, hướng phát triển.**
10. **Phụ lục:** prompt, siêu tham số, bảng chi phí, hướng dẫn chấm tay.

### 11.2 Slide (khoảng 20 slide)
1. Tiêu đề
2. Bài toán và động lực
3. RAG và nút thắt rerank
4. RQ và đóng góp
5. BioASQ
6. Dựng kho ứng viên
7. Metadata
8. Soát nhãn
9. Phân tích ngữ liệu
10. Pipeline
11. Sáu thế hệ reranker (nhấn mạnh BiLSTM-ESIM)
12. Bảng chính E2
13. RQ1 metadata
14. Jev và GPT 2×2
15. **Pareto chi phí–chất lượng**
16. Soát nhãn RQ3
17. RAG trọn vẹn RQ4
18. So với kết quả công bố
19. Ca tốt và ca không tốt
20. Kết luận và hạn chế

Thêm một biểu đồ **"dòng thời gian phương pháp"**: trục ngang là năm ra đời của phương pháp, trục dọc là nDCG@10.

---

## 12. Cấu trúc code

> ⚠️ **Thư mục `Lab2` hiện chứa đồ án AML** (repo `Chung10102004/atbmtt`). **Code NLP không đặt chung repo đó.** TODO: tạo repo riêng, ví dụ `~/Documents/NLP/bioasq-metarr/`, rồi chuyển file này sang. Cần người dùng xác nhận vị trí trước khi viết code.

```
bioasq-metarr/
├── NLP_PROJECT_PLAN.md         # file này
├── pyproject.toml              # uv, Python ≥ 3.11, khóa phiên bản thư viện
├── .env.example                # OPENAI_API_KEY, TYPESAFE_API_KEY, NCBI_API_KEY, NCBI_EMAIL
├── configs/
│   ├── models.yaml             # model ID GPT / Jev / HF, ghim phiên bản
│   ├── pricing.yaml            # giá kèm ngày lấy
│   └── experiments/*.yaml      # cấu hình E1–E6
├── data/                       # không commit: raw BioASQ, cache PubMed, corpus, index
├── src/
│   ├── data/                   # bioasq_loader, splits, leakage_check, pubmed_search, pubmed_fetch,
│   │                           # mesh_validate, query_metadata, build_corpus, audit, package
│   ├── retrieval/              # bm25, medcpt_dense, rrf
│   ├── rerank/                 # base (rerank(query, candidates) -> [(pmid, score)]),
│   │                           # lambdamart, bilstm_esim, cross_encoder, gpt_listwise, jev, metadata_boost
│   ├── rag/                    # prompts, generate, context_filter, gate
│   ├── eval/                   # ir_metrics, qa_metrics, bioasq_official, significance, judge
│   └── utils/                  # cache (hash → JSONL), cost_logger, cost_guard, io
├── scripts/                    # build_dataset.py, run_experiment.py, bench_latency.py, make_tables.py
├── annotation/                 # file chấm tay + hướng dẫn cho nhóm
├── notebooks/                  # 01_corpus_analysis, 05_error_analysis, 06_cost_quality
├── results/<exp>/<run_id>/     # config.yaml, metrics.json, run.trec, calls.jsonl
├── report/                     # tiểu luận, hình, bảng sinh tự động
└── tests/
```

---

## 13. Lộ trình và tiêu chí hoàn thành

Deadline: **TODO, người dùng cung cấp**. Ước lượng 5 tuần cộng tuần 0.

### Giai đoạn 0 — Chuẩn bị (tuần 0)
- [ ] Người dùng: đăng ký BioASQ; tạo key OpenAI, TypeSafe, NCBI; đặt giới hạn chi tiêu; xác nhận vị trí repo.
- [ ] Tạo repo, `pyproject.toml`, `.env.example`, `configs/`.
- [ ] `cache`, `cost_logger`, `cost_guard`, `pricing.yaml`.
- [ ] Kiểm tra `jev-reranker`: chạy `examples/eval.py` trên NanoHotpotQA. **Đạt khi** nDCG@10 xấp xỉ 0,969.
- [ ] Chạy thử GPT structured outputs và Batch API trên 5 câu.

### Giai đoạn 1 — Dữ liệu C1 (tuần 1–2)
- [ ] Loader BioASQ, chia tập, kiểm tra rò rỉ. **Đạt khi** có báo cáo số câu trùng và số câu bị loại.
- [ ] `esearch` có q1/q2 và giới hạn ngày; `efetch` kèm metadata; `corpus.jsonl`.
- [ ] Index BM25 và MedCPT; RRF top-100. **E1 hoàn thành.**
- [ ] Metadata câu hỏi qua GPT Batch; kiểm tra MeSH; file chấm 100 câu cho nhóm.
- [ ] Notebook phân tích ngữ liệu (mục 4.8), có đủ hình.

### Giai đoạn 2 — Reranker local (tuần 3)
- [ ] R0, R1 (LambdaMART), R3, R4 × M0/M1/M2.
- [ ] R2 BiLSTM-ESIM, 3 seed. **Đạt khi** MAP trên dev cao hơn R0, hoặc đã phân tích được lý do nếu không cao hơn.
- [ ] Code chấm chính thức + bootstrap.

### Giai đoạn 3 — Reranker API (tuần 3–4)
- [ ] R5 GPT listwise, R6 Jev × M0/M1/M2. **E2 hoàn thành.**
- [ ] E3: 2×2, listwise và pointwise, thiên vị vị trí.

### Giai đoạn 4 — RAG, nhãn, chi phí (tuần 4)
- [ ] E5 với mọi kịch bản; dò ngưỡng Jev trên dev.
- [ ] E4: ứng viên cần soát → Jev và GPT → file chấm cho nhóm → `qrels+` → chấm lại.
- [ ] E6: bench độ trễ và thông lượng; Pareto; bảng quyết định.
- [ ] Phân tích lỗi (notebook 05).

### Giai đoạn 5 — Viết (tuần 5)
- [ ] Bảng và hình sinh tự động từ `results/`.
- [ ] Tiểu luận và slide theo mục 11. Mọi con số phải truy được về file kết quả.
- [ ] Đóng gói BioASQ-MetaRR (mục 4.7) nếu giấy phép cho phép.

---

## 14. Rủi ro và dự phòng

| Rủi ro | Dự phòng |
|---|---|
| Đăng ký BioASQ bị chậm | Chuyển sang **MultiHop-RAG** (609 bài báo, 2.556 câu, 4 loại câu hỏi, metadata có sẵn), giữ nguyên pipeline. Mốc so: [Multi-Meta-RAG](https://arxiv.org/abs/2406.13213), với bge-large MAP@10 0,2687 → 0,3293 và Hits@10 0,7490 → 0,8909 |
| `esearch` ra ít kết quả | Dùng truy vấn q2 (OR); cho GPT sinh truy vấn từ khóa; tăng `retmax` |
| Recall của kho thấp | Báo cáo như một cận trên; phân tích theo loại câu hỏi |
| Vượt chi phí API | Cache, rerank top-50, cost guard, Batch API, chạy tập con 100 câu cho các cấu hình đắt |
| API Jev đổi hoặc bị giới hạn tốc độ | Ghim phiên bản; retry có backoff; ghi lại ngày chạy |
| BiLSTM yếu | Đây là kết quả có ý nghĩa, phân tích nguyên nhân: OOV, độ dài, thiếu tiền huấn luyện |
| Judge và generator cùng hãng | Hầu hết metric dùng nhãn gốc; judge chỉ cho ideal answer, khác model, có chấm tay |
| Giấy phép dữ liệu | Chỉ phát hành ID, metadata và script |

---

## 15. Việc nhóm phải tự làm

Claude không làm thay được, hoặc không nên làm thay, các việc sau:

1. **Tài khoản và key:** đăng ký BioASQ; tạo API key OpenAI, TypeSafe, NCBI; nạp tiền và đặt giới hạn chi tiêu.
2. **Chấm tay.** Phải do người làm thì phương pháp mới hợp lệ. Claude chuẩn bị file chấm và hướng dẫn.
   - Metadata câu hỏi: 100 câu.
   - Soát nhãn: ít nhất 100 ca.
   - Kiểm chứng LLM-judge: 50–100 câu.
3. **Duyệt và chịu trách nhiệm** nội dung tiểu luận, slide; tự thuyết trình và trả lời câu hỏi.
4. **Kiểm tra quy định của môn về việc dùng công cụ AI,** và ghi rõ trong tiểu luận nếu môn yêu cầu.
5. **Duyệt các lần chạy API** có chi phí ước tính vượt ngưỡng trong mục 16.

---

## 16. Quy tắc làm việc cho Claude

- **Đầu mỗi phiên đọc file này.** Cuối phiên cập nhật checklist ở mục 13 và nhật ký ở mục 17.
- **Không chỉnh gì trên test.** Mọi ngưỡng, siêu tham số, prompt đều chọn trên dev.
- **Mọi lệnh gọi API** đi qua `cache` và `cost_logger`. Trước khi chạy một job có chi phí ước tính **trên 5 USD** (sửa trong `configs/`), chạy `--dry-run` để ước tính, **báo người dùng và chờ đồng ý**.
- **Ghim phiên bản:** khóa thư viện; model ID trong `configs/models.yaml`; ghi ngày chạy vào mỗi `results/<run_id>/config.yaml`.
- **Seed cố định** (0/1/2) cho mô hình có huấn luyện.
- **Không commit** dữ liệu thô, abstract, cache API hay key.
- **Báo cáo trung thực:** kết quả âm tính và thí nghiệm thất bại vẫn ghi lại. Không có con số nào trong tiểu luận mà không truy được về file kết quả.
- Mục nào có **TODO: xác minh** thì phải kiểm tra lại trước khi dùng số liệu hoặc API tương ứng.

---

## 17. Nhật ký quyết định

| Ngày | Quyết định | Lý do |
|---|---|---|
| 2026-10-25 | Đề tài: RAG y tế, có thành phần LSTM | Theo yêu cầu của môn |
| 2026-10-26 | Bỏ ViHealthQA và PubMedQA, **chọn BioASQ Task 13b** | ViHealthQA chỉ có 1 đoạn đúng mỗi câu, yếu cho rerank. BioASQ có nhiều bài đúng mỗi câu, snippet, đáp án, metadata MeSH và kết quả công bố gần đây |
| 2026-10-26 | Dự phòng: MultiHop-RAG | Dễ làm, có metadata, có loại câu null |
| 2026-11-06 | Trọng tâm là **dữ liệu nhóm tự xây (C1) và phân tích**; pipeline RAG là hạ tầng | Theo định hướng của người dùng |
| 2026-11-06 | **Chỉ dùng GPT API**; Jev qua `jev-reranker` (hotchpotch, MIT) | Ràng buộc tài nguyên |
| 2026-11-06 | Mọi reranker dùng chung **top-50** | Vừa ngân sách token của Jev (26k), so công bằng |
| 2026-11-06 | Thêm **E6 chi phí và tốc độ**, RQ5 | Để quyết định dùng Jev hay GPT ở vai trò nào |
| 2026-11-06 | LSTM = **BiLSTM-ESIM reranker** | Yêu cầu của môn; đúng trọng tâm rerank |

---

## 18. Tài liệu tham khảo

- BioASQ 2025 overview: https://arxiv.org/pdf/2508.20554 · Tasks 13b: https://ceur-ws.org/Vol-4038/paper_1.pdf
- Kết quả 13b: http://participants-area.bioasq.org/results/13b/phaseAplus/ · http://participants-area.bioasq.org/results/13b/phaseB/
- BioASQ 2024 overview: https://arxiv.org/pdf/2508.20532
- BEIR: https://arxiv.org/pdf/2104.08663
- MIRAGE / MedRAG: https://arxiv.org/pdf/2402.13178
- RankGPT: https://arxiv.org/abs/2304.09542
- jev-reranker: https://huggingface.co/blog/hotchpotch/introducing-jev-reranker · https://github.com/hotchpotch/jev-reranker
- Các bài về Jev:
  - Elastic: https://www.elastic.co/search-labs/blog/ecommerce-search-reranking-llm-alternative-jev
  - Qdrant: https://qdrant.tech/blog/jevjitsu/
  - Supermemory: https://supermemory.ai/blog/jev-memory-context-engineering/
  - Hindsight: https://hindsight.vectorize.io/blog/2026/09/24/adding-jev-reranker-what-we-learned
- MultiHop-RAG: https://arxiv.org/pdf/2401.15391 · Multi-Meta-RAG: https://arxiv.org/abs/2406.13213
