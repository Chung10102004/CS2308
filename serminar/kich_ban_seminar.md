# BioRerank — Kịch bản seminar từng slide

> **Chủ đề:** BioRerank: Evaluating Document Reranking Models for Biomedical Information Retrieval
> **Loại buổi:** seminar về chủ đề (không phải bảo vệ đồ án, không demo).
> **Trọng tâm:** **reranking**: vì sao cần, bài toán là gì, các cách xây reranker, và cách đánh giá. Dữ liệu y sinh chỉ là **phòng thử nghiệm** để có số liệu thật.
> **Thời lượng:** khoảng 22 phút trình bày, sau đó hỏi đáp. 25 slide chính và phụ lục. Có phương án rút còn 20 hoặc 15 phút.
> **Cập nhật:** 11/11/2026. Đã có số của GPT-6 Luna (đồng đội chạy) và Jev (chạy ngày 11/11).
> Mọi con số đều lấy từ `report/tables/`, `results/` hoặc từ bảng của Abdallah et al. 2025. Nguồn ghi ở cuối mỗi slide. Hai số tính riêng ngày 11/11, chưa có trong `report/tables/`, là **trần của reranker** và **tốc độ BM25**; cách tính ghi ở phụ lục A11–A12.

---

## 0. Khung chung của bài

### Thông điệp một câu
Nói ở slide 2 và nhắc lại ở slide 25:

> *"Reranking tồn tại vì không có mô hình nào vừa đủ nhanh để quét cả kho, vừa đủ kỹ để xếp đúng mười bài đầu. Ba mươi năm qua, bài toán gần như không đổi (xếp lại một danh sách ứng viên), chỉ có cách xây hàm xếp hạng thay đổi. Bước tiến lớn nhất đến từ **những gì mô hình đã học**, còn **cách quyết định** chủ yếu làm thay đổi **chi phí**. Và muốn so reranker thì phải **cùng ứng viên, cùng bộ nhãn**."*

### Cấu trúc
| Phần | Câu hỏi trả lời | Slide |
|---|---|---|
| Mở đầu | Reranker ảnh hưởng lớn đến đâu? | 1–2 |
| **A. Tại sao phải có reranking** | Vì sao không dùng một mô hình duy nhất? | 3–4 |
| **B. Bài toán reranking** | Định nghĩa, ba cách quyết định, ba cách học, không gian thiết kế | 5–8 |
| C. Đánh giá reranker | Đo bằng gì, thử trên đâu, bẫy ở đâu | 9–11 |
| **D. Hành trình 7 thế hệ** | Mỗi thế hệ xây hàm xếp hạng thế nào | 12–20 |
| E. Nhìn lại | Xu hướng, điều bất ngờ, chọn reranker trong thực tế | 21–24 |
| Kết | Ba điều rút ra | 25 |

### Khuôn của mỗi slide thế hệ (phần D)
1. Hình ảnh đời thường.
2. Thuật toán cốt lõi (3–4 dòng).
3. **Cách học**: hàm mất mát hoặc nguồn tri thức.
4. **Cách quyết định** (huy hiệu `TỪNG BÀI` / `CẶP · NHÓM NHỎ` / `CẢ DANH SÁCH`) và **chi phí** cho mỗi truy vấn.
5. Điểm trên phòng thử nghiệm.
6. Vấn đề còn để lại, cũng là lý do có thế hệ sau.

### Câu hỏi xuyên suốt
Topic 26 của TREC-COVID: *"what are the initial symptoms of Covid-19?"*. Mỗi slide thế hệ mở thêm một ô điểm (nDCG@10, thang 0–100). Slide 21 lật cả bảng.

| BM25 | LambdaMART | BiLSTM-ESIM | bge-v2-m3 | MedCPT | MonoT5 | Qwen3 | GPT-6 Luna | Jev |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 55 | 51 | 37 | 100 | **3** (đổi sang từ khóa: 40) | 86 | 100 | 56 | 47 |

Nguồn: `results/e1/e1_per_query.json`; MedCPT với từ khóa: `results/runs/trec-covid/test/medcpt_ce.Q-kw.trec`.

### Quy ước màu (cả bộ slide, khớp các hình trong `report/figures/`)
- **Xám:** số đã công bố (Abdallah et al. 2025).
- **Cam:** nhóm chạy lại model có trong bài báo.
- **Xanh:** model nhóm chạy mới.

### Phân thời gian

| Phần | Slide | Thời gian | Người trình bày |
|---|---|---:|---|
| Mở đầu | 1–2 | 1,2' | |
| A. Tại sao phải có reranking | 3–4 | 2,3' | |
| B. Bài toán reranking | 5–8 | 3,8' | |
| C. Đánh giá reranker | 9–11 | 2,3' | |
| D. Hành trình 7 thế hệ | 12–20 | 8,4' | |
| E. Nhìn lại | 21–24 | 3,3' | |
| Kết | 25 | 0,8' | |
| **Tổng** | | **khoảng 22'** | |

**Rút còn 20 phút:**
- chuyển slide 24 (câu hỏi mở) vào phụ lục;
- gộp slide 16 (MedCPT) vào slide 15 thành một ý;
- nói nhanh slide 12–13.

**Rút còn 15 phút:** làm như trên, và thêm:
- gộp slide 6 và 7 (cách quyết định và cách học);
- gộp slide 17 và 18;
- gộp slide 19 và 20;
- bỏ slide 10 (chỉ còn một dòng trong slide 9);
- gộp slide 22 vào slide 21.

---

## Slide 1 — Tiêu đề

**Thời lượng:** 20 giây

**Trên slide**
- `SEMINAR NLP · CS2308`
- Tiêu đề: **BioRerank: Evaluating Document Reranking Models for Biomedical Information Retrieval**
- Phụ đề: *Reranking qua bảy thế hệ: từ đếm từ khóa đến mô hình quyết định*
- Tên nhóm, MSSV.
- Minh họa: hình phễu (kho → 100 ứng viên → top-10) cạnh một dải thời gian 1994 → 2026.

**Lời nói**
> "Chào thầy cô và các bạn. Chủ đề của nhóm em là **reranking**: bước xếp hạng lại kết quả tìm kiếm. Nhóm em sẽ trả lời ba câu hỏi: vì sao phải có bước này, bài toán thực chất là gì, và trong ba mươi năm qua người ta đã xây reranker theo những cách nào. Dữ liệu y sinh là nơi nhóm em thử nghiệm để có số liệu thật."

---

## Slide 2 — Cùng 100 bài, điểm từ 3 đến 100

**Thời lượng:** 50 giây

**Trên slide**
- Câu hỏi in to: *"What are the initial symptoms of Covid-19?"*
- Dòng nhỏ: *Cùng 100 bài ứng viên cho mọi mô hình.*
- Hai con số lớn, **chưa ghi tên model**: `3 / 100` và `100 / 100`.
- Ba lý do xếp hạng khó (đều là vấn đề chung của tìm kiếm):
  1. **Cùng nghĩa, khác chữ:** "initial symptoms" và "first clinical manifestations".
  2. **Câu hỏi khác từ khóa:** người hỏi viết câu đầy đủ, nhiều hệ thống quen với từ khóa ("coronavirus early symptoms").
  3. **Từ mới:** "covid-19" không có trong các từ điển làm trước 2019.

**Lời nói**
> "Một câu hỏi: triệu chứng ban đầu của Covid-19 là gì. Hệ thống lấy ra 100 bài báo, và **cùng 100 bài đó** được đưa cho nhiều mô hình xếp lại. Một mô hình đạt 100 trên 100 điểm, một mô hình khác chỉ đạt 3. Ứng viên giống hệt nhau; khác biệt nằm hoàn toàn ở **bước xếp lại**, tức reranker.
>
> Xếp hạng khó vì cùng một ý có thể viết bằng chữ khác hẳn, vì người hỏi và hệ thống quen với hai kiểu diễn đạt khác nhau, và vì luôn có từ mới.
>
> Thông điệp của nhóm em: reranking tồn tại vì không mô hình nào vừa nhanh vừa kỹ; bài toán không đổi suốt ba mươi năm, chỉ cách xây hàm xếp hạng thay đổi; và muốn so reranker thì phải cùng ứng viên, cùng bộ nhãn."

**Chuyển sang slide 3**
> "Câu hỏi đầu tiên: tại sao lại cần một bước 'xếp lại'? Sao không dùng luôn mô hình tốt nhất để tìm?"

**Nguồn:** `results/e1/e1_per_query.json` (topic 26); `data/raw/trec_covid/topics-rnd5.xml` (trường query, narrative).

---

## Slide 3 — Tại sao phải có reranking (1): không mô hình nào vừa nhanh vừa kỹ

**Thời lượng:** 1 phút 10 giây

**Trên slide**
- **Đo thật:** BM25 quét cả kho TREC-COVID (171.331 bài) và trả về top-100 trong **16 ms** (trung vị, một luồng CPU).
- **Nếu để mô hình mạnh đọc cả kho cho một câu hỏi** (ngoại suy tuyến tính từ thời gian đọc 100 bài):

| Mô hình | Thời gian / 1 câu hỏi | Chi phí API / 1 câu hỏi |
|---|---:|---:|
| BM25 (đo thật) | **0,016 s** | 0 |
| MedCPT cross-encoder | khoảng 18 phút | — |
| bge-reranker-v2-m3 | khoảng 65 phút | — |
| Jev | khoảng 31 phút | khoảng 2,8 USD |
| Qwen3-Reranker-4B | khoảng 12 giờ | — |
| GPT-6 Luna | khoảng 14 giờ | khoảng 9,6 USD |

- **Vì sao chênh nhau hơn 200 nghìn lần:**
  - BM25 dùng **chỉ mục ngược** dựng sẵn từ trước. Lúc hỏi, nó chỉ chạm vào các bài có chứa từ của câu hỏi.
  - Mô hình đọc chung (câu hỏi, bài) **không dựng sẵn được**, vì điểm phụ thuộc vào câu hỏi. Mỗi câu hỏi mới phải chạy lại với từng bài.
- **Lời giải: phễu nhiều tầng**
  ```
  171.331 bài ──BM25, 16 ms──▶ 100 ứng viên ──reranker, 0,6–29 s──▶ top-10 ──▶ (RAG) LLM đọc 5 bài
  ```
  - Tầng trên **rẻ**, nhắm tới **không bỏ sót** (recall).
  - Tầng dưới **đắt**, nhắm tới **đúng ở đầu danh sách** (precision ở top).

**Lời nói**
> "Nhóm em đo thử: BM25 quét toàn bộ 171 nghìn bài và trả về 100 bài đầu chỉ trong 16 mili-giây. Giờ thử để một mô hình mạnh đọc toàn bộ kho cho **một** câu hỏi: cross-encoder mất từ 18 phút đến hơn một tiếng; mô hình ngôn ngữ lớn mất 12 đến 14 tiếng, và nếu gọi qua API thì gần 10 đô cho một câu hỏi.
>
> Vì sao chênh nhau tới hơn 200 nghìn lần? BM25 có chỉ mục dựng sẵn, giống mục lục cuối sách: muốn tìm chữ nào thì lật thẳng tới trang có chữ đó. Còn mô hình mạnh phải đọc **câu hỏi cùng với từng bài**, mà câu hỏi thì chỉ biết lúc người dùng gõ, nên không chuẩn bị trước được.
>
> Lời giải là một cái phễu. Tầng một rẻ, lọc thật nhanh, chỉ cần không bỏ sót. Tầng hai đắt, nhưng chỉ đọc kỹ 100 bài để đưa bài đúng lên đầu. Tầng hai chính là reranker."

**Chuyển sang slide 4**
> "Nhưng nếu tầng một đã lấy ra đúng 100 bài liên quan, xếp lại có thật sự đáng công không?"

**Nguồn:**
- BM25: đo ngày 11/11 bằng Pyserini, index `beir-v1.0.0-trec-covid.flat`, 50 truy vấn (phụ lục A12).
- Thời gian đọc 100 bài và chi phí: `report/tables/e4_cost.md` (p50), ngoại suy × 1.713.

---

## Slide 4 — Tại sao phải có reranking (2): tầng một xếp đầu danh sách chưa tốt, mà LLM chỉ đọc vài bài đầu

**Thời lượng:** 1 phút 10 giây

**Trên slide**
- **Ba lý do tầng một xếp đầu danh sách kém:**
  1. **Khớp chữ, không khớp nghĩa** (BM25).
  2. **Tóm bài trước khi biết câu hỏi.** Tìm kiếm bằng vector (bi-encoder) nén mỗi bài thành một vector từ trước, nên mất các chi tiết tương tác giữa câu hỏi và bài ("so ảnh thẻ").
  3. **Mục tiêu khác:** tầng một được thiết kế để không bỏ sót, không phải để xếp đúng 10 bài đầu.
- **Bằng chứng: khoảng trống nằm ngay trong 100 ứng viên.** "Trần" là điểm đạt được nếu xếp lại **hoàn hảo** đúng 100 bài BM25 đã lấy ra:

| Bộ | BM25 | Trần (xếp lại hoàn hảo) | Reranker tốt nhất | Đã lấp được |
|---|---:|---:|---:|---:|
| TREC-COVID | 59,47 | **97,48** | 85,45 | **68%** khoảng trống |
| SciFact | 67,89 | **92,65** | 79,77 | 48% |
| NFCorpus | 32,18 | **54,39** | 38,60 | 29% |

- Ví dụ (topic 6, *"rapid testing for Covid-19"*):
  - Bài đầu của BM25: *"Coronavirus disease 2019 in children…"* ✗
  - Bài đầu sau rerank: *"Types of Assays for SARS-CoV-2 Testing: A Review"* ✓
- **Trong RAG**, LLM chỉ đọc vài bài đầu:
  - ngữ cảnh dài thì tốn token;
  - LLM dùng thông tin ở **giữa** ngữ cảnh kém hơn ở đầu và cuối (Liu et al., *Lost in the Middle*, TACL 2024).

  → Thứ tự quan trọng, không chỉ việc có mặt trong danh sách.

**Lời nói**
> "Tầng một xếp đầu danh sách chưa tốt vì ba lý do. BM25 chỉ khớp chữ. Các hệ thống tìm bằng vector thì tóm mỗi bài thành một vector **trước khi** biết câu hỏi, giống so hai tấm ảnh thẻ thay vì phỏng vấn trực tiếp. Và tầng một vốn được thiết kế để không bỏ sót, chứ không để xếp đúng 10 bài đầu.
>
> Nhóm em đo 'trần': nếu chỉ **xếp lại hoàn hảo** đúng 100 bài BM25 đã lấy, không thêm bài nào, thì điểm lên được bao nhiêu. Trên TREC-COVID, từ 59 lên tới 97. Nghĩa là gần như toàn bộ chất lượng còn thiếu nằm ở **thứ tự**, không nằm ở việc thiếu bài. Reranker tốt nhất hiện nay đã lấp được 68% khoảng trống đó.
>
> NFCorpus thì khác: trần chỉ 54, vì 70 trên 323 câu hỏi không có bài đúng nào trong 100 ứng viên. Ở đó lỗi nằm ở tầng một, và reranker không cứu được.
>
> Cuối cùng là lý do thời sự nhất: trong RAG, mô hình ngôn ngữ chỉ đọc vài bài đầu, và nó còn đọc phần giữa ngữ cảnh kém hơn phần đầu. Vì vậy bài nào đứng đầu quyết định câu trả lời."

**Chuyển sang slide 5**
> "Vậy nói chính xác, bài toán reranking là gì?"

**Nguồn:**
- Trần: tính ngày 11/11 từ `results/runs/<bộ>/test/bm25.trec` và qrels (phụ lục A11).
- Reranker tốt nhất: `report/tables/e1_main.md`.
- Topic 6: `report/tables/error_cases.md`.
- Liu et al. 2024, *Lost in the Middle: How Language Models Use Long Contexts*, TACL.

---

## Slide 5 — Bài toán reranking: định nghĩa

**Thời lượng:** 1 phút 10 giây

**Trên slide**
- **Ký hiệu**
  - Kho tài liệu D (TREC-COVID: |D| = 171.331), truy vấn q.
  - Tầng một (retriever R, ở đây là BM25) trả về danh sách ứng viên C_q = (d₁, …, d_k), với **k = 100 ≪ |D|**.
  - Nhãn mức liên quan rel_q(d) ∈ {0, 1, 2}, có sẵn trong benchmark; bài chưa được chấm tính là 0.
- **Định nghĩa.** Reranker là một hàm f nhận câu hỏi và danh sách ứng viên, trả về một **hoán vị** của danh sách đó:
  ```
  π = f(q, C_q)          π là một cách sắp xếp lại C_q
  Mục tiêu:  max_f  E_q [ nDCG@10(π, rel_q) ]
  ```
- **Ràng buộc then chốt:** reranker **chỉ đổi thứ tự**, không thêm và không bớt bài. Vì vậy:
  - có **trần** (slide 4);
  - chất lượng của tầng một quyết định giới hạn trên của tầng hai.
- **Khác với truy xuất tầng một:**

| | Tầng một (retrieval) | Tầng hai (reranking) |
|---|---|---|
| Phạm vi | Cả kho (hàng trăm nghìn đến hàng triệu bài) | k ứng viên (thường 20–1.000) |
| Ràng buộc | Phải mã hóa tài liệu trước, tra cứu bằng index | Được đọc chung (câu hỏi, bài), tốn kém cũng được |
| Mục tiêu | Không bỏ sót (Recall@k) | Đúng ở đầu danh sách (nDCG@10) |
| Ví dụ | BM25, bi-encoder (DPR, MedCPT retriever) | cross-encoder, LLM, Jev |

**Lời nói**
> "Nói chính xác: có một kho tài liệu rất lớn và một câu hỏi. Tầng một lấy ra một danh sách k ứng viên, ở đây là 100. Reranker là một hàm nhận câu hỏi và 100 ứng viên này, rồi trả về **một cách sắp xếp lại** chúng. Mục tiêu là điểm nDCG@10 trung bình cao nhất, tức là bài đúng nằm ở trên cùng.
>
> Điều quan trọng nhất trong định nghĩa: reranker **không được thêm bài mới**. Nó chỉ đổi thứ tự. Vì vậy nó có trần, và trần đó do tầng một quyết định.
>
> Đổi lại, vì chỉ phải xử lý 100 bài, reranker được phép làm những việc tốn kém mà tầng một không làm nổi, như đọc câu hỏi và bài cùng một lúc."

**Chuyển sang slide 6**
> "Hàm f này có thể được xây theo ba cách quyết định rất khác nhau."

**Nguồn:** `NLP_PROJECT_PLAN.md` mục 5; Abdallah et al. 2025 (thiết lập BM25 top-100).

---

## Slide 6 — Ba cách quyết định: từng bài, từng cặp, cả danh sách

**Thời lượng:** 1 phút

**Trên slide** (ba cột, mỗi cột một hình nhỏ)

| | **Từng bài** (pointwise) | **Cặp / nhóm nhỏ** (pairwise / setwise) | **Cả danh sách** (listwise) |
|---|---|---|---|
| Hàm | s(q, d) ∈ ℝ, rồi sắp xếp theo s | P(dᵢ ≻ dⱼ \| q), rồi gộp thắng thua | f(q, d₁…d_k) → hoán vị, hoặc s(q, dᵢ \| C_q) |
| Mô hình nhìn thấy | 1 bài | 2 bài (hoặc vài bài) | Nhiều bài cùng lúc |
| Số lượt chạy với k = 100 | 100 lượt, **chạy song song** | 4.950 cặp (all-pairs) | Cửa sổ trượt w = 20, s = 10: **9 lượt nối tiếp**; Jev: **1 request** (chia nhóm khi quá dài) |
| Ví dụ | BM25, LambdaMART, BiLSTM, cross-encoder, MonoT5, Qwen3 | PRP, Setwise | RankGPT, RankZephyr, ListT5, GPT-6 Luna, Jev |
| Điểm yếu | Không thấy bài khác, nên không biết bài này hơn hay kém bài kia | Đắt (k²), có thể không bắc cầu (A > B > C > A) | Giới hạn ngữ cảnh (phải trượt hoặc chia nhóm), **phụ thuộc thứ tự đưa vào**, có thể trả thiếu hoặc trùng ID |

**Lời nói**
> "Có ba cách để hàm f ra quyết định.
>
> Cách một: **chấm từng bài**. Mỗi bài được cho một điểm độc lập rồi sắp xếp. Đơn giản, chạy song song được, nhưng mô hình không bao giờ thấy các bài khác.
>
> Cách hai: **so từng cặp**, 'A hay B tốt hơn', như đấu vòng tròn. Chính xác hơn về mặt so sánh, nhưng 100 bài cần gần 5.000 cặp.
>
> Cách ba: **nhìn cả danh sách** rồi xếp. Mô hình thấy bối cảnh, nhưng danh sách dài không vừa một lần đọc, nên phải trượt cửa sổ hoặc chia nhóm, và kết quả có thể phụ thuộc vào thứ tự đưa bài vào.
>
> Ở mỗi thế hệ phía sau, góc slide sẽ có huy hiệu cho biết mô hình quyết định theo cách nào."

**Chuyển sang slide 7**
> "Cách quyết định là chuyện lúc dùng. Còn lúc học thì sao?"

**Nguồn:** Sun et al. 2023 (RankGPT, cửa sổ 20/10); Qin et al. 2023 (PRP); Zhuang et al. 2024 (Setwise); `report/tables/e4_cost.md`.

---

## Slide 7 — Ba cách học: ba họ hàm mất mát

**Thời lượng:** 1 phút

**Trên slide**

| Họ | Hàm mất mát | Ý nghĩa |
|---|---|---|
| **Từng bài** | L = −[y·log σ(s) + (1−y)·log(1−σ(s))] | Phân loại liên quan / không liên quan (monoBERT, MonoT5 học sinh "true"/"false") |
| **Cặp** (RankNet, 2005) | L = log(1 + e^{−(sᵢ − sⱼ)}) với dᵢ ≻ dⱼ | Bài đúng phải có điểm cao hơn bài sai |
| **Danh sách** (softmax, kiểu ListNet 2007) | L = −log( e^{s(d⁺)} / Σ_{d ∈ {d⁺, d₁⁻…d_n⁻}} e^{s(d)} ) | Trong một nhóm, bài đúng phải nổi lên trên tất cả |
| **LambdaRank / LambdaMART** | Gradient của RankNet nhân với \|ΔnDCG\| | Xếp sai ở top-10 bị phạt nặng; xếp sai ở hạng 90 gần như không bị phạt |
| **Chưng cất** (RankZephyr) | Học bắt chước hoán vị do LLM lớn (GPT) tạo ra | Biến LLM đắt thành LLM nhỏ, chạy local |

- **Học theo kiểu nào không có nghĩa là quyết định theo kiểu đó.**
  - LambdaMART học bằng LambdaRank, BiLSTM-ESIM học bằng softmax trên nhóm 1 bài đúng + 7 bài sai, nhưng cả hai đều **chấm từng bài** khi dùng.
  - Có những mô hình **không học rerank** mà chỉ được hỏi: RankGPT (prompt), Jev (tiêu chí viết bằng câu).

**Lời nói**
> "Lúc huấn luyện cũng có ba họ tương ứng. Học từng bài: coi như bài toán phân loại liên quan hay không. Học theo cặp: chỉ cần bài đúng có điểm cao hơn bài sai. Học theo danh sách: trong một nhóm, bài đúng phải vượt lên tất cả.
>
> LambdaRank thêm một ý rất hay: phạt theo **mức thiệt hại cho nDCG**. Đảo sai hai bài ở top-10 bị phạt nặng; đảo sai ở hạng 90 thì gần như không sao, vì người dùng chẳng bao giờ đọc tới đó.
>
> Hai điều cần nhớ. Thứ nhất, học kiểu danh sách không có nghĩa là quyết định kiểu danh sách: hai mô hình của nhóm em học bằng hàm danh sách nhưng vẫn chấm từng bài. Thứ hai, các thế hệ mới nhất thậm chí **không học rerank**, mà chỉ được hỏi bằng lời."

**Chuyển sang slide 8**
> "Ghép tất cả lại, ta có một không gian thiết kế, và bảy thế hệ reranker là bảy điểm trong không gian đó."

**Nguồn:** Burges et al. 2005 (RankNet); Cao et al. 2007 (ListNet); Burges 2010 (LambdaMART); Pradeep et al. 2023 (RankZephyr); `src/rerank/lambdamart.py`; `src/kaggle_tasks/bilstm.py`.

---

## Slide 8 — Không gian thiết kế và bản đồ bảy thế hệ

**Thời lượng:** 40 giây

**Trên slide**
- **Năm trục thiết kế của một reranker:**

| Trục | Các lựa chọn |
|---|---|
| Đọc gì | chữ trùng · đặc trưng thủ công · vector từ tĩnh · ngữ cảnh tiền huấn luyện · LLM |
| Đọc thế nào | tách riêng (bi-encoder) · đọc chung (cross-encoder) |
| Quyết định | từng bài · cặp / nhóm nhỏ · cả danh sách |
| Học từ đâu | không học · nhãn trong miền · tiền huấn luyện + dữ liệu rerank tổng quát · prompt / tiêu chí bằng câu |
| Trả ra gì | điểm · xác suất một token · chuỗi hoán vị · xác suất đã hiệu chỉnh |

- **Bản đồ bảy thế hệ** (mục lục của phần D):

| Đời | Năm | Model | Đọc gì | Quyết định |
|---|---|---|---|---|
| 1 | 1994 | BM25 | Chữ trùng | Từng bài |
| 2 | 2010 | LambdaMART | Đặc trưng thủ công | Từng bài |
| 3 | 2017 | BiLSTM-ESIM | Vector từ tĩnh + attention | Từng bài |
| 4 | 2019–2024 | Cross-encoder (bge, mxbai, MedCPT) | Ngữ cảnh tiền huấn luyện | Từng bài |
| 5 | 2020 | MonoT5 | Ngữ cảnh, đầu ra "true" | Từng bài |
| 6 | 2023–2026 | LLM (Qwen3, RankGPT, GPT-6 Luna) | Kiến thức của LLM | Từng bài / cặp / danh sách |
| 7 | 2026 | Jev | Không công bố | Cả danh sách, một lượt |

**Lời nói**
> "Mọi reranker đều trả lời năm câu hỏi thiết kế: đọc gì, đọc tách hay đọc chung, quyết định theo cách nào, học từ đâu, và trả ra cái gì. Bảy thế hệ mà nhóm em sắp đi qua chính là bảy cách trả lời năm câu hỏi đó. Trước khi đi, cần thống nhất cách chấm điểm."

**Chuyển sang slide 9**
> "Chấm một bảng xếp hạng thế nào?"

**Nguồn:** tổng hợp từ các slide 6–7; `src/eval/systems.py` (năm, thế hệ).

---

## Slide 9 — nDCG@10: bài đúng phải nằm ở trên

**Thời lượng:** 50 giây

**Trên slide**
- Công thức (gain tuyến tính, như BEIR và trec_eval):
  ```
  DCG@10  = Σ_{i=1..10}  rel_i / log2(i + 1)
  nDCG@10 = DCG@10 / DCG@10 của thứ tự lý tưởng
  ```
- Ví dụ tính tay, câu hỏi có 2 bài đúng:
  - Hai bài đúng ở **hạng 1 và 3**: DCG = 1 + 1/2 = 1,5; lý tưởng ≈ 1,63 → **nDCG ≈ 0,92**.
  - Hai bài đúng ở **hạng 9 và 10**: DCG ≈ 0,59 → **nDCG ≈ 0,36**.
- **Quy ước so sánh:** mọi reranker xếp lại **cùng một danh sách BM25 top-100**, giống bảng của Abdallah et al. (EMNLP Findings 2025, 22 phương pháp, 40 biến thể). Nhờ đó số của nhóm đặt được ngay cạnh số đã công bố.
- So hai hệ thống: paired bootstrap 10.000 lần, hiệu chỉnh Holm, p < 0,05.

**Lời nói**
> "Thước đo là nDCG@10, khớp đúng với mục tiêu trong định nghĩa. Cùng hai bài đúng trong top-10: nằm ở hạng 1 và 3 thì được 0,92; nằm ở hạng 9 và 10 thì chỉ 0,36. Nghĩa là thước đo này thưởng cho **thứ tự**, đúng việc reranker làm.
>
> Quy ước quan trọng: mọi reranker xếp lại cùng 100 ứng viên, giống bài so sánh lớn nhất hiện nay. Khi nói A hơn B, nhóm em đều kiểm định thống kê."

**Chuyển sang slide 10**
> "Nhóm em thử trên ba bộ dữ liệu y sinh."

**Nguồn:** `src/eval/ir_metrics.py`; Abdallah et al. 2025, arXiv:2508.16757.

---

## Slide 10 — Phòng thử nghiệm: ba bộ y sinh, ba kiểu truy vấn

**Thời lượng:** 30 giây

**Trên slide**

| | TREC-COVID | NFCorpus | SciFact |
|---|---|---|---|
| Kiểu truy vấn | Câu hỏi | Từ khóa (trung vị 2 từ) | Câu khẳng định khoa học |
| Số truy vấn / số bài | 50 / 171.331 | 323 / 3.633 | 300 / 5.183 |
| Ai gán nhãn | NIST | Tự động từ link | Chuyên gia |

- **Vì sao chọn:** nhãn công khai, không cần ai chấm thêm; cùng thiết lập với bảng 40 biến thể của Abdallah, nên so trực tiếp được. Ba kiểu truy vấn khác nhau sẽ cho thấy reranker mạnh hay yếu ở đâu.
- Bộ phụ **SciFact-Open** (nhãn đã được chuyên gia soát lại) dùng cho slide 11.

**Lời nói**
> "Phòng thử nghiệm là ba bộ y sinh trong benchmark BEIR, ứng với ba kiểu truy vấn: câu hỏi, từ khóa rất ngắn, và câu khẳng định khoa học. Nhóm em chọn chúng vì nhãn có sẵn và vì bài so sánh lớn nhất hiện nay cũng dùng đúng ba bộ này với đúng thiết lập đó."

**Chuyển sang slide 11**
> "Khi chạy thật, nhóm em gặp hai cái bẫy mà ai làm đánh giá reranker cũng nên biết."

**Nguồn:** `results/data_report/corpus_stats.json`; Thakur et al. 2021 (BEIR).

---

## Slide 11 — Hai cái bẫy khi đánh giá reranker

**Thời lượng:** 1 phút

**Trên slide**

**Bẫy 1: cách đưa văn bản vào reranker.** Nhóm chạy lại bài báo trước khi so (tái lập):
- BM25 khớp tuyệt đối với bài báo (59,47 và 67,89).
- bge-reranker-v2-m3 trên TREC-COVID:

| Cách nhập | nDCG@10 |
|---|---:|
| Tiêu đề + abstract | 78,57 |
| Chỉ abstract | 74,26 |
| Bài báo công bố | 74,79 |

→ Bảng công bố **trộn hai cách nhập** giữa các dòng. Riêng điều này đã lệch khoảng 4 điểm, lớn hơn khoảng cách giữa nhiều mô hình.

**Bẫy 2: nhãn thiếu.** Không ai chấm hết mọi bài trong kho.
- Tỷ lệ bài trong top-10 của BM25 đã có nhãn (Judged@10): **91% / 30% / 8,8%**.
- SciFact-Open: chuyên gia soát lại, số cặp bằng chứng tăng từ **209 lên 460**. Khi chấm bằng nhãn đã soát:
  - cross-encoder tăng 3,5 đến 6,8 điểm, BM25 chỉ tăng 1,4;
  - **Qwen3 và MedCPT đổi chỗ ở hạng 1**;
  - **6 cặp hệ thống bị đảo thứ tự** (Kendall τ = 0,78, 11 hệ thống).
- TREC-COVID, nếu chỉ dùng nhãn vòng 1: τ = 0,56, **17 cặp bị đảo** (13 hệ thống).

Hình: `report/figures/fig_e3_scifact_open.png` hoặc `fig_e3_trec_covid_rounds.png`.

**Lời nói**
> "Bẫy thứ nhất: chỉ riêng việc có đưa tiêu đề vào reranker hay không đã lệch 4 điểm, và bảng công bố trộn cả hai cách. Nếu không chạy lại để kiểm, ta sẽ so táo với cam.
>
> Bẫy thứ hai: nhãn thiếu. Bài chưa ai chấm bị tính là sai. Khi chuyên gia chấm thêm, số bằng chứng tăng hơn gấp đôi, hạng 1 đổi chủ, 6 cặp mô hình đảo thứ tự. Reranker neural thường đưa lên những bài mà hệ thống cũ chưa từng đưa ra, nên chúng bị 'phạt oan' nhiều nhất.
>
> Bài học: so reranker phải cùng ứng viên, cùng cách nhập, và phải biết nhãn đầy đủ tới đâu."

**Chuyển sang slide 12**
> "Có sân chơi chung rồi. Giờ đi qua bảy thế hệ, bắt đầu từ năm 1994."

**Nguồn:** `report/tables/e0_reproduction.md`; `report/tables/e3_labels.md`; `results/data_report/corpus_stats.json`.

---

## Slide 12 — Đời 1 · BM25 (1994): đếm từ khóa · `TỪNG BÀI`

**Thời lượng:** 45 giây

**Trên slide**
- Hình ảnh: **người cầm bút dạ quang** tô các từ trùng với câu hỏi.
- Thuật toán:
  ```
  score(q, d) = Σ_{t ∈ q} IDF(t) · tf·(k1+1) / (tf + k1·(1 − b + b·|d|/avgdl))
  ```
  - Từ hiếm (IDF cao) đáng giá hơn.
  - Lặp nhiều lần thì có thêm điểm nhưng ít dần (k1 = 0,9).
  - Bài dài bị trừ nhẹ (b = 0,4).
- **Cách học:** không học. **Chi phí:** chỉ mục ngược, 16 ms cho cả kho.
- Điểm: **59,47 / 32,18 / 67,89**, TB **53,18**. Ô câu hỏi xuyên suốt: **55**.
- Vai trò kép: vừa là **mốc so sánh**, vừa là **tầng một chọn ứng viên**, nên quyết định trần của mọi reranker phía sau (slide 4).

**Lời nói**
> "BM25 ra đời năm 1994 và đến nay vẫn là tầng một của hầu hết hệ thống tìm kiếm. Nó như người cầm bút dạ quang: tô từ trùng, từ hiếm cho nhiều điểm, lặp lại thì thêm ít dần, bài dài bị trừ nhẹ. Không cần học, cực nhanh, nhưng chỉ thấy chữ, không thấy nghĩa. Và vì nó chọn 100 ứng viên, nó cũng quyết định trần của mọi reranker phía sau."

**Chuyển sang slide 13**
> "BM25 chỉ có một tín hiệu. Khi có nhiều tín hiệu, ai quyết định cái nào quan trọng hơn? Để máy học."

**Nguồn:** `report/tables/e1_main.md`; Robertson et al., TREC-3 (1994).

---

## Slide 13 — Đời 2 · LambdaMART (2010): học cách trộn tín hiệu · `TỪNG BÀI`

**Thời lượng:** 50 giây

**Trên slide**
- Hình ảnh: **giám khảo chấm theo bảng tiêu chí**. Không đọc bài, chỉ nhìn 11 con số.
- 11 đặc trưng: điểm/hạng BM25, TF-IDF, độ giống theo MedCPT bi-encoder, từ trùng với truy vấn và với tiêu đề, độ dài bài, độ dài truy vấn…
- Thuật toán:
  ```
  lặp 1.000 lần: thêm một cây quyết định
      lực đẩy bài i = Σ |ΔnDCG nếu đổi chỗ i, j| × mức độ đang xếp sai
      cây mới học cách sửa lực đẩy đó
  ```
- **Cách học:** LambdaRank (slide 7). Học theo danh sách, nhưng **quyết định từng bài**.
- Điểm: **71,37 / 35,67 / 75,97**, TB **61,00**, tăng 8 điểm so với BM25. Hơn BM25 ở 33/50 câu TREC-COVID. Ô câu hỏi xuyên suốt: **51**.
- Lưu ý: **68%** sức mạnh đến từ đặc trưng MedCPT, một mô hình neural.

**Lời nói**
> "Thế hệ hai là learning-to-rank. LambdaMART không đọc văn bản: mỗi bài được tóm thành 11 con số, và mô hình là 1.000 cây quyết định cộng dồn, cây sau sửa lỗi cây trước. Hàm học nhắm thẳng vào nDCG, như ở slide hàm mất mát.
>
> Tăng 8 điểm so với BM25. Nhưng 68% sức mạnh đến từ một đặc trưng là điểm của một mô hình neural. Mô hình chỉ giỏi bằng các tín hiệu mà con người nghĩ ra và đưa vào."

**Chuyển sang slide 14**
> "Đặc trưng vẫn do người nghĩ ra. Máy có tự đọc văn bản được không?"

**Nguồn:** `report/tables/e1_main.md`; `results/e1/lambdamart_train.json`; `report/tables/error_cases.md`.

---

## Slide 14 — Đời 3 · BiLSTM-ESIM (2017): tự đọc, so từng chữ · `TỪNG BÀI`

**Thời lượng:** 1 phút

**Trên slide**
- Hình ảnh: **người đọc từng chữ và dò bảng đối chiếu**.
- Kiến trúc:
  ```
  từ → vector (BioWordVec 200 chiều, cố định)
     → BiLSTM đọc xuôi và ngược
     → soft alignment:  e_ij = a_i · b_j ;   ã_i = Σ_j softmax(e_ij) · b_j
     → so sánh [a; ã; a − ã; a ⊙ ã]   (giống ở đâu, khác ở đâu)
     → BiLSTM tổng hợp → avg + max pool → MLP → điểm
  ```
- **Cách học:** softmax trên nhóm 1 bài đúng + 7 bài sai, **học từ đầu** (không tiền huấn luyện mô hình).
- Điểm: **55,38 / 26,44 / 72,30**, TB **51,38**, **thấp hơn BM25**. Chỉ hơn BM25 trên SciFact.
- Ô câu hỏi xuyên suốt: **37**.
- Vì sao thua:
  - **78%** câu hỏi TREC-COVID có từ không có trong từ điển;
  - truy vấn NFCorpus khoảng 2 từ;
  - chỉ khoảng 3.200 truy vấn để học.

**Lời nói**
> "Thế hệ ba: mạng nơ-ron tự đọc văn bản. ESIM, năm 2017, đọc như một người dò bảng đối chiếu: với mỗi từ của câu hỏi, tìm những từ giống nhất trong bài, ghi lại chỗ khớp và chỗ lệch, rồi tổng hợp thành điểm. Không cần ai thiết kế đặc trưng.
>
> Nhưng kết quả **thấp hơn BM25**. Lý do: vector từ cố định, từ điển làm trước COVID nên 78% câu hỏi có từ lạ, và mô hình phải học từ con số 0 với khoảng 3.200 câu hỏi. Tự đọc được, nhưng chưa đủ kiến thức nền."

**Chuyển sang slide 15**
> "Lời giải của thế hệ sau: cho mô hình **đọc trước hàng tỉ câu**, rồi mới dạy nó xếp hạng."

**Nguồn:** `report/tables/e1_main.md`; `report/tables/improvements.md`; `results/data_report/bilstm_oov.json`; Chen et al., ACL 2017.

**Ghi chú cho người nói** (chỉ nói khi bị hỏi): bản v2 thêm vector cho từ lạ đoán từ ngữ cảnh (*à la carte*) và kênh khớp từ y hệt, đạt 56,54 / 26,73 / 70,15. Bản chỉ có vector đoán từ ngữ cảnh đạt 60,44 trên TREC-COVID (1 seed) nhưng không được chọn, vì tập dev không có từ COVID.

---

## Slide 15 — Đời 4 · Cross-encoder (2019 →): tiền huấn luyện, đọc chung · `TỪNG BÀI`

**Thời lượng:** 1 phút

**Trên slide**
- Hai cách đặt cạnh nhau:
  - **Bi-encoder** = so **ảnh thẻ**: vector(câu hỏi) · vector(bài). Mã hóa bài trước được, nên hợp với tầng một.
  - **Cross-encoder** = **phỏng vấn trực tiếp**: `[CLS] câu hỏi [SEP] tiêu đề. abstract [SEP]` → Transformer → điểm. Mọi chữ nhìn mọi chữ (self-attention); phải chạy lại cho từng cặp, nên hợp với tầng hai.
- **Cách học:**
  1. Tiền huấn luyện trên hàng tỉ câu.
  2. Học rerank trên hàng triệu cặp (câu hỏi, đoạn văn). monoBERT dùng loss từng bài.
- **Chi phí:** 100 lượt, chạy theo lô trên GPU, từ 0,6 đến 2,3 giây.
- Điểm (zero-shot, nhóm không huấn luyện thêm):

| Model | TB 3 bộ |
|---|---:|
| bge-reranker-base | 57,24 |
| bge-reranker-large | 60,75 |
| bge-reranker-v2-m3 | 62,08 |
| mxbai-rerank-base | 63,52 |

- Ô câu hỏi xuyên suốt (bge-v2-m3): **100**. bge-v2-m3 hơn BM25 ở 40/50 câu.

**Lời nói**
> "Thế hệ bốn là bước nhảy lớn nhất. Từ BERT năm 2019, mô hình được đọc trước hàng tỉ câu để hiểu nghĩa theo ngữ cảnh, rồi mới học xếp hạng.
>
> Có hai cách dùng, và đây chính là lý do của kiến trúc hai tầng. Bi-encoder giống so ảnh thẻ: tóm bài trước được, nhanh, nên dùng ở tầng một. Cross-encoder giống phỏng vấn: đọc câu hỏi cạnh bài, mọi chữ nhìn mọi chữ, chính xác nhưng phải chạy cho từng cặp, nên dùng ở tầng hai.
>
> Từ 51 điểm của BiLSTM lên 57 đến 64 điểm, mà **không cần học gì thêm trên dữ liệu y sinh**. Một chi tiết: mxbai bản base lại hơn bge bản large. To hơn chưa chắc tốt hơn."

**Chuyển sang slide 16**
> "Nếu dữ liệu học quan trọng như vậy, thì học đúng chuyên ngành có tốt hơn không?"

**Nguồn:** `report/tables/e1_main.md`; `report/tables/e4_cost.md`; Nogueira & Cho 2019 (monoBERT).

---

## Slide 16 — Đời 4 · Dữ liệu học quyết định reranker giỏi ở đâu (MedCPT, 2023) · `TỪNG BÀI`

**Thời lượng:** 50 giây

**Trên slide**
- MedCPT: cross-encoder giống slide trước, nhưng **học từ log tìm kiếm PubMed**, tức các cặp (người dùng gõ gì, bấm vào bài nào).
- Điểm: **68,79 / 34,68 / 79,58**.
  - SciFact 79,58: cao hơn mọi dòng đã công bố.
  - TREC-COVID 68,79: thua bge-v2-m3 (78,57) gần 10 điểm.
- Cùng 100 ứng viên, chỉ đổi **dạng truy vấn** đưa vào:

| Đưa vào MedCPT | TREC-COVID | Topic 26 |
|---|---:|---:|
| Câu hỏi (mặc định) | 68,79 | **3** |
| Từ khóa của NIST | **75,43** (+6,6) | **40** |

**Lời nói**
> "Đây là lời giải cho con số 3 ở đầu bài. MedCPT học từ hàng trăm triệu lượt tìm kiếm thật trên PubMed, nơi người dùng **gõ từ khóa**. Khi gặp câu hỏi đầy đủ, nó chỉ được 3 điểm. Đổi sang từ khóa, cùng 100 ứng viên đó, lên 40.
>
> Bài học cho reranking nói chung: **reranker giỏi ở đúng kiểu câu hỏi nó đã học**. Kiểu câu hỏi quan trọng hơn chuyên ngành."

**Chuyển sang slide 17**
> "Đến đây reranker vẫn cần dữ liệu xếp hạng để học. Nếu mô hình đủ lớn, có thể chỉ cần **hỏi nó có hay không**?"

**Nguồn:** `report/tables/e1_main.md`; `report/tables/e2_metadata.md`; Jin et al. 2023 (MedCPT).

---

## Slide 17 — Đời 5–6 · Từ "true" đến "yes": MonoT5 và Qwen3 · `TỪNG BÀI`

**Thời lượng:** 50 giây

**Trên slide**
- **MonoT5 (2020):** rerank trở thành một câu hỏi đúng/sai.
  ```
  "Query: … Document: … Relevant:"  →  điểm = log P("true")
  ```
  - Cách học: dạy mô hình sinh "true" / "false".
  - Điểm 74,08 / 35,06 / 73,24, TB 60,79. Ô câu hỏi xuyên suốt: **86**.
- **Qwen3-Reranker-4B (2025):** cùng ý đó với LLM 4 tỉ tham số.
  ```
  "Judge whether the Document meets the requirements… answer only yes or no"
  điểm = logit("yes") − logit("no")
  ```
  - Điểm **85,00 / 37,37 / 79,35**, TB **67,24**. Hơn BM25 ở 44/50 câu. Ô câu hỏi xuyên suốt: **100**.
- **Chi phí:** Qwen3 mất **25 giây/truy vấn** trên GPU T4 (100 lượt chạy mô hình 4B).

**Lời nói**
> "MonoT5 có một ý tưởng khéo: thay vì bắt mô hình xuất ra một con số, hỏi nó 'bài này có liên quan không' và đo xem nó muốn trả lời 'true' chắc đến mức nào. Ý tưởng này mở đường cho việc dùng mô hình sinh văn bản để xếp hạng.
>
> Qwen3-Reranker làm đúng như vậy với một LLM 4 tỉ tham số: đo 'yes' trội hơn 'no' bao nhiêu. Được 67,24, cao hơn mọi dòng công bố cũ. Cái giá là 25 giây cho một câu hỏi."

**Chuyển sang slide 18**
> "Cả hai vẫn chấm từng bài. Cho LLM nhìn nhiều bài cùng lúc thì sao?"

**Nguồn:** `report/tables/e1_main.md`; `report/tables/e4_cost.md`; Nogueira et al. 2020; model card Qwen3-Reranker.

---

## Slide 18 — Đời 6 · LLM so cặp và xếp cả danh sách · `CẶP` / `CẢ DANH SÁCH`

**Thời lượng:** 1 phút 10 giây

**Trên slide**
- **Pairwise (PRP, 2023):** hỏi "A hay B liên quan hơn?" cả hai chiều. 100 bài cần 4.950 cặp.
- **Setwise (2024):** đưa vài bài, hỏi "bài nào tốt nhất?", lặp lại như sắp xếp nổi bọt.
- **Listwise (RankGPT, 2023), cửa sổ trượt từ dưới lên:**
  ```
  xếp bài 81–100 → giữ 10 bài tốt nhất → ghép với bài 71–80 → … → bài 1–20
  = 9 lượt nối tiếp; bài tốt ở hạng 95 vẫn có thể "nổi" lên hạng 1
  ```
- **Cách học:** RankGPT không học gì (chỉ prompt); RankZephyr chưng cất từ GPT; ListT5 học trên nhóm nhỏ rồi đấu loại.
- Bảng điểm (TB 3 bộ):

| Model | Cách quyết định | TB | Nguồn |
|---|---|---:|---|
| RankGPT gpt-3.5 | danh sách | 60,91 | công bố |
| Setwise Flan-T5-XXL | nhóm nhỏ | 62,27 | công bố |
| RankZephyr 7B | danh sách | 64,14 | công bố |
| RankGPT gpt-4 (chỉ top-30) | danh sách | 66,31 | công bố |
| ListT5-3B | danh sách | 66,47 | công bố |
| **GPT-6 Luna** | **danh sách** | **67,94** | **nhóm** |

- GPT-6 Luna: **85,45 / 38,60 / 79,77**. Cao nhất bảng, nhưng **29 giây/truy vấn** (9 lượt nối tiếp) và **5,61 USD / 1.000 truy vấn**. Ô câu hỏi xuyên suốt: **56**.

**Lời nói**
> "Khi có LLM kiểu ChatGPT, người ta thử cho mô hình nhìn nhiều bài cùng lúc. So từng cặp thì chính xác nhưng 100 bài cần gần 5.000 cặp. RankGPT đưa 20 bài và bảo xếp lại; 100 bài không vừa một lần nên dùng cửa sổ trượt từ dưới lên, mất 9 lượt. Điều hay là một bài tốt bị BM25 vứt xuống hạng 95 vẫn có thể leo lên hạng 1.
>
> Nhóm em chạy theo cách này với GPT-6 Luna: 67,94, **cao nhất cả bảng**. Nhưng gần 30 giây một câu hỏi, và 9 lượt phải chạy nối tiếp. Trên câu hỏi của chúng ta, Luna chỉ được 56, ngang BM25. Điểm trung bình cao nhất không có nghĩa câu nào cũng tốt nhất."

**Chuyển sang slide 19**
> "Nhìn cả danh sách thì tốt, nhưng đắt và chậm. Có cách nào **thấy cả danh sách mà chỉ cần một lượt**?"

**Nguồn:** `report/tables/e1_main.md`; `report/tables/e4_cost.md`; `results/e1/luna_run_summary.json`; Sun et al. 2023; Qin et al. 2023; Zhuang et al. 2024; Pradeep et al. 2023; Yoon et al. 2024.

---

## Slide 19 — Đời 7 · Jev (2026): quyết định, không sinh chữ · `CẢ DANH SÁCH, MỘT LƯỢT`

**Thời lượng:** 1 phút

**Trên slide**
- Jev của TypeSafe AI, công bố 15/09/2026. TypeSafe gọi đây là **"System One model"**, theo khái niệm phán đoán nhanh của Kahneman.
- Hình ảnh: **phát phiếu cho cả hội đồng**. Cả 100 bài đặt lên bàn, mỗi bài một phiếu đúng/sai, Jev điền hết các phiếu trong một lượt.
- Cơ chế:
  ```
  state     = { query, documents: { doc_0 … doc_99 } }
  questions = { doc_i: Noul("Is documents.doc_i relevant to query?",
                            true: "…", false: "…") }
  answers   = Jev(state, questions)      # một lượt, không sinh từng token
  điểm_i    = P(true) đã hiệu chỉnh  →  sắp xếp giảm dần
  ```
- So với các thế hệ trước:

| | RankGPT / Luna | Qwen3 | **Jev** |
|---|---|---|---|
| Nhìn thấy | 20 bài mỗi lượt | 1 bài | Cả danh sách |
| Đầu ra | Chuỗi hoán vị (phải đọc lại) | logit yes − no | **P(true) cho từng bài** |
| Số lượt / truy vấn | 9 nối tiếp | 100 | **1** (chia nhóm khi quá dài) |
| Tiêu chí | Prompt | Instruction cố định | **Tiêu chí bằng câu, đổi không cần học lại** |

- TypeSafe công bố: huấn luyện bằng RLCD (Reinforcement Learning for Calibrated Decisions); 70–500 ms mỗi lần gọi; 0,042 USD / 1 triệu token đầu vào, token đầu ra miễn phí.
- **Hộp đen:** không công bố kiến trúc, số tham số, dữ liệu huấn luyện.

**Lời nói**
> "Thế hệ bảy rất mới: Jev, ra mắt tháng 9 năm nay. Ý tưởng là: để xếp hạng, không cần mô hình **viết** ra câu trả lời, chỉ cần nó **quyết định**.
>
> Giống phát phiếu cho một hội đồng: cả 100 bài đặt lên bàn, mỗi bài một phiếu 'có liên quan không'. Jev điền tất cả phiếu trong một lượt, mỗi phiếu là một xác suất. Nó nhìn cả danh sách như RankGPT nhưng không phải trượt 9 lần, và không phải viết chữ rồi đọc lại. TypeSafe nói xác suất này đã được hiệu chỉnh, giống dự báo '70% mưa' thì khoảng 7 trên 10 ngày mưa thật.
>
> Jev là hộp đen. Nhóm em chỉ đánh giá được đầu ra, và kiểm chứng lời hứa của họ."

**Chuyển sang slide 20**
> "Lời hứa có đúng không?"

**Nguồn:** [TypeSafe docs – System One](https://docs.typesafe.ai/concepts/system-one); [TypeSafe blog](https://typesafe.ai/blog/introducing-system-one-models-and-jev); thư viện `jev-reranker` 0.1.2 (`src/rerank/jev.py`).

---

## Slide 20 — Jev: ngang LLM về chất lượng, nhanh hơn khoảng 25 lần

**Thời lượng:** 1 phút

**Trên slide**

| Model | Cách quyết định | TREC-COVID | NFCorpus | SciFact | TB | Thời gian/truy vấn | USD / 1.000 truy vấn |
|---|---|---:|---:|---:|---:|---:|---:|
| GPT-6 Luna | danh sách, 9 lượt | 85,45 | 38,60 | 79,77 | 67,94 | 28,9 s | 5,61 |
| **Jev** | **danh sách, 1 lượt** | **84,41** | **38,24** | **79,14** | **67,27** | **1,1 s** | **1,62** |
| Qwen3-4B | từng bài | 85,00 | 37,37 | 79,35 | 67,24 | 25,0 s | 2,48* |
| bge-reranker-v2-m3 | từng bài | 78,57 | 33,69 | 73,99 | 62,08 | 2,3 s | 0,22* |

\* mô hình chạy local: USD quy theo giá thuê GPU T4 (ước lượng); API: chi phí thật từ log.

- **Ba mô hình đầu không khác nhau có ý nghĩa thống kê** trên cả 3 bộ (bootstrap + Holm). Ngoại lệ duy nhất: Luna hơn Qwen3 trên NFCorpus.
- Jev hơn bge-v2-m3 **4,6–5,8 điểm** (có ý nghĩa trên NFCorpus và SciFact; TREC-COVID p = 0,08 vì chỉ có 50 câu).
- Model thực tế: **jev-1.14.0**. 673 truy vấn tốn 1.243 request (trung bình 1,8 request/truy vấn vì tự chia nhóm). Tổng chi phí **1,09 USD**.
- Ô câu hỏi xuyên suốt: **47**.

**Lời nói**
> "Jev đạt 67,27, nằm trong nhóm dẫn đầu cùng Luna và Qwen3, và kiểm định cho thấy **ba mô hình này không khác nhau có ý nghĩa**. Khác biệt nằm ở chi phí: Jev 1,1 giây một câu hỏi, Luna gần 29 giây, Qwen3 25 giây.
>
> Đây là điểm đáng chú ý nhất về reranking của buổi hôm nay: hai mô hình **cùng nhìn cả danh sách**, Luna và Jev, có chất lượng như nhau nhưng thời gian chênh 25 lần, chỉ vì một bên sinh chữ qua 9 lượt, một bên ra quyết định trong một lượt.
>
> Tuy vậy, câu hỏi của chúng ta là ngoại lệ: Jev chỉ được 47, Luna 56, trong khi các mô hình chấm từng bài đạt 100. Một câu chưa đủ để kết luận; nhóm em sẽ kiểm tra tiếp."

**Chuyển sang slide 21**
> "Bảy thế hệ. Giờ đặt tất cả cạnh nhau."

**Nguồn:** `report/tables/e1_main.md`; `report/tables/e4_cost.md`; `results/api_logs/jev__*.jsonl`; kiểm định chạy bằng `src/eval/significance.py` trên `results/e1/e1_per_query.json`.

**Ghi chú cho người nói:**
- Độ trễ đo từ máy nhóm, gồm cả mạng: 1,1 s chia cho 1,8 request ≈ 0,6 s mỗi request; TypeSafe công bố 70–500 ms.
- Số này mới là bảng chính E1, tiêu chí chung "Is the document relevant to the query?".

---

## Slide 21 — Nhìn lại hành trình

**Thời lượng:** 1 phút

**Trên slide**

| Đời | Năm | Đọc gì | Học từ đâu | Quyết định | Thời gian/truy vấn | TB 3 bộ | Topic 26 |
|---|---|---|---|---|---:|---:|---:|
| 1 BM25 | 1994 | Chữ trùng | Không | Từng bài | 0,016 s (cả kho) | 53,18 | 55 |
| 2 LambdaMART | 2010 | Đặc trưng thủ công | Nhãn trong miền (LambdaRank) | Từng bài | ≈ 0 + đặc trưng | 61,00 | 51 |
| 3 BiLSTM-ESIM | 2017 | Vector từ tĩnh + attention | Nhãn trong miền, học từ đầu | Từng bài | 0,06 s | 51,38 | 37 |
| 4 Cross-encoder | 2019–24 | Ngữ cảnh tiền huấn luyện | Dữ liệu rerank tổng quát, zero-shot | Từng bài | 0,6–2,3 s | 57–64 | 3–100 |
| 5 MonoT5 | 2020 | Như trên, đầu ra "true" | Như trên | Từng bài | 4,3 s | 60,79 | 86 |
| 6 LLM | 2023–26 | Kiến thức LLM | Prompt / chưng cất | Từng bài / cặp / danh sách | 25–29 s | 67,24–67,94 | 56–100 |
| 7 Jev | 2026 | Không công bố | Tiêu chí bằng câu | Danh sách, một lượt | 1,1 s | 67,27 | 47 |

**Năm xu hướng:**
1. **Đọc gì:** chữ → đặc trưng → biểu diễn tự học → ngữ cảnh tiền huấn luyện → kiến thức LLM.
2. **Học từ đâu:** không học → nhãn trong miền → tiền huấn luyện + zero-shot → chỉ cần lời dặn.
3. **Quyết định:** từng bài → so cặp, xếp danh sách (khi có LLM) → danh sách nhưng một lượt.
4. **Trả ra gì:** điểm → xác suất một token → chuỗi hoán vị → quyết định có kiểu kèm xác suất.
5. **Chi phí:** tăng tới 25–29 giây ở đời 6; **đời 7 kéo xuống còn khoảng 1 giây**.

**Lời nói**
> "Đặt bảy thế hệ cạnh nhau, có năm xu hướng. Mô hình đọc ngày càng sâu hơn: từ chữ, đến nghĩa, đến kiến thức. Dữ liệu cần thì ngày càng ít: từ phải có nhãn trong miền, đến chỉ cần một câu dặn. Chi phí tăng dần đến LLM, rồi thế hệ mới nhất kéo nó xuống lại.
>
> Và nhìn cột cuối, câu hỏi của chúng ta: điểm nhảy từ 3 đến 100, không đi theo năm. Đó là chủ đề của slide sau."

**Chuyển sang slide 22**
> "Tiến bộ có, nhưng không đi thẳng."

**Nguồn:** `report/tables/e1_main.md`; `report/tables/e4_cost.md`; `results/e1/e1_per_query.json`; hình `report/figures/fig_timeline.png`.

---

## Slide 22 — Tiến bộ không đi thẳng

**Thời lượng:** 50 giây

**Trên slide**
- Hình chính: `report/figures/fig_e1_ranking.png` (số của nhóm đặt cạnh 40 dòng công bố).
- Ba điểm "không đi thẳng":
  1. **Mới hơn chưa chắc tốt hơn:** BiLSTM (2017) thấp hơn BM25 (1994). Bước nhảy đến từ **tiền huấn luyện**, không phải từ việc dùng mạng nơ-ron.
  2. **Chuyên ngành chưa chắc tốt hơn:** MedCPT thua bge trên câu hỏi, thắng trên claim. Kiểu truy vấn đã học mới là yếu tố quyết định.
  3. **Nhìn cả danh sách chưa chắc tốt hơn:** Luna, Jev (danh sách) và Qwen3 (từng bài) ngang nhau về thống kê. Cách quyết định chủ yếu đổi **chi phí**.
- Trích dẫn: Abdallah et al. (2025) nhận xét reranker dùng LLM mạnh với truy vấn quen thuộc, nhưng khả năng tổng quát sang truy vấn mới thay đổi nhiều, còn mô hình gọn nhẹ cạnh tranh về hiệu quả.

**Lời nói**
> "Ba điều không đi theo đường thẳng. Một: mới hơn chưa chắc tốt hơn; thứ tạo ra bước nhảy là tiền huấn luyện. Hai: chuyên ngành chưa chắc tốt hơn; quan trọng là mô hình đã học kiểu câu hỏi nào. Ba: nhìn cả danh sách chưa chắc tốt hơn chấm từng bài; ở nhóm dẫn đầu, khác biệt là giá tiền và thời gian, không phải chất lượng. Điều này khớp với nhận xét của bài so sánh Abdallah năm 2025."

**Chuyển sang slide 23**
> "Vậy nếu phải chọn reranker cho một hệ thống thật thì chọn thế nào?"

**Nguồn:** `report/figures/fig_e1_ranking.png`; Abdallah et al. 2025 (abstract).

---

## Slide 23 — Chọn reranker trong thực tế: theo ngân sách độ trễ

**Thời lượng:** 50 giây

**Trên slide**
- Hình: `report/figures/fig_e4_pareto.png` (chi phí và chất lượng).

| Ngân sách (100 ứng viên) | Lựa chọn | TB nDCG@10 | Ghi chú |
|---|---|---:|---|
| Gần như 0 | BM25 thuần | 53,18 | Không có reranker |
| < 1 giây | MedCPT (0,64 s, GPU) | 61,02 | Phụ thuộc kiểu truy vấn |
| 1–2 giây | **Jev (1,1 s, API)** hoặc mxbai (1,7 s, GPU) | 67,27 / 63,52 | Jev: chất lượng ngang LLM |
| Không gấp (offline) | GPT-6 Luna, Qwen3 | 67,94 / 67,24 | 25–29 s/truy vấn |

- Ba nút điều chỉnh khác khi thiết kế:
  - **Độ sâu k:** k lớn thì trần cao hơn nhưng chi phí tăng tuyến tính.
  - **Phễu nhiều tầng:** cross-encoder lọc 100 → 20, rồi LLM chỉ đọc 20 (giống RankGPT gpt-4 chỉ xếp top-30). Nhóm chưa đo.
  - **Dữ liệu nhạy cảm:** dùng API (Luna, Jev) nghĩa là gửi văn bản ra ngoài; mô hình local giữ dữ liệu tại chỗ.

**Lời nói**
> "Trong hệ thống thật, câu hỏi không phải 'mô hình nào tốt nhất' mà là 'trong ngân sách thời gian này, mô hình nào tốt nhất'. Dưới 1 giây: cross-encoder nhỏ. Khoảng 1 đến 2 giây: Jev cho chất lượng ngang LLM. Nếu xử lý offline, không gấp: LLM.
>
> Ngoài chọn mô hình, còn ba nút điều chỉnh: lấy bao nhiêu ứng viên, có xếp thành nhiều tầng không, và dữ liệu có được phép gửi ra ngoài không. Với dữ liệu y tế, nút cuối rất quan trọng."

**Chuyển sang slide 24**
> "Còn nhiều câu hỏi nhóm em chưa trả lời được."

**Nguồn:** `report/tables/e4_cost.md`; `report/figures/fig_e4_pareto.png`.

---

## Slide 24 — Câu hỏi còn mở

**Thời lượng:** 40 giây

**Trên slide**
1. **Cùng một mô hình, đổi cách quyết định:** Jev chạy được cả listwise lẫn pointwise, nên là thí nghiệm có kiểm soát (ước khoảng 1,1 USD). Thí nghiệm này cũng giúp giải thích ca topic 26.
2. **Nhãn thiếu với LLM:** phần chấm lại bằng nhãn đã soát của SciFact-Open mới có 11 mô hình local, chưa có Luna và Jev.
3. **LLM có thể đã "thấy" đề:** các bộ BEIR công khai từ 2021. Cần truy vấn mới để kiểm tra (Abdallah 2025: FutureQueryEval).
4. **Tiêu chí viết riêng:** dùng mô tả "thế nào là liên quan" của NIST làm tiêu chí cho Jev thay vì câu chung.
5. **Xác suất của Jev có thật sự được hiệu chỉnh?** So với nhãn có sẵn (biểu đồ hiệu chỉnh), không tốn thêm tiền API.

**Lời nói**
> "Câu hỏi quan trọng nhất còn mở: muốn biết nhìn cả danh sách có giúp không, phải giữ nguyên mô hình và chỉ đổi cách quyết định. Jev cho phép làm đúng điều đó. Ngoài ra còn lo ngại chung là mô hình lớn có thể đã thấy các bộ dữ liệu này khi huấn luyện."

**Chuyển sang slide 25**
> "Nhóm em xin tóm lại bằng ba điều."

**Nguồn:** `report/tables/e3_labels.md`; `scripts/run_api.py --dry-run`.

---

## Slide 25 — Ba điều rút ra · Hỏi đáp

**Thời lượng:** 50 giây

**Trên slide**
1. **Reranking tồn tại vì đánh đổi tốc độ và độ kỹ.** BM25 quét cả kho trong 16 ms; mô hình mạnh đọc cả kho mất từ 18 phút đến 14 giờ. Chỉ cần đọc kỹ 100 ứng viên đã lấp được tới 68% khoảng trống chất lượng.
2. **Bài toán không đổi, hàm xếp hạng thay đổi.**
   - Bước nhảy lớn nhất là tiền huấn luyện (51 → 57–64 → khoảng 67).
   - Dữ liệu học phải khớp kiểu truy vấn (MedCPT: 3 → 40).
   - Cách quyết định chủ yếu đổi **chi phí** (1 s so với 29 s ở cùng chất lượng).
3. **Đánh giá reranker phải cùng ứng viên, cùng cách nhập, biết nhãn đầy đủ tới đâu.** Cách nhập lệch 4 điểm; nhãn thiếu đảo 6 cặp.

*Cảm ơn thầy cô và các bạn · Hỏi đáp*

**Lời nói**
> "Tóm lại ba điều. Một: reranking tồn tại vì không mô hình nào vừa nhanh vừa kỹ; chỉ cần đọc kỹ 100 ứng viên đã lấy lại phần lớn chất lượng còn thiếu. Hai: suốt ba mươi năm, bài toán vẫn là xếp lại một danh sách; cái thay đổi là hàm xếp hạng, và bước tiến lớn nhất đến từ những gì mô hình đã học, còn cách quyết định chủ yếu đổi chi phí. Ba: muốn so reranker thì phải cùng sân chơi, cùng bộ nhãn.
>
> Nhóm em xin cảm ơn thầy cô và các bạn đã lắng nghe, và mời mọi người đặt câu hỏi."

---

## Phụ lục (chỉ mở khi bị hỏi)

| Slide | Nội dung | Lấy từ |
|---|---|---|
| A1 | Giả mã đầy đủ 7 thế hệ (BM25, LambdaMART λ, ESIM, cross-encoder, MonoT5, RankGPT cửa sổ trượt, PRP/Setwise, Qwen3, Jev, RRF) | Trao đổi thiết kế slide |
| A2 | nDCG@10 chi tiết; Judged@10; nDCG condensed (bỏ bài chưa có nhãn trước khi chấm) | `src/eval/ir_metrics.py` |
| A3 | Kendall τ (mốc tham khảo 0,9 của Voorhees); paired bootstrap + Holm | `src/eval/rank_correlation.py`, `significance.py` |
| A4 | Bảng đầy đủ: mọi dòng của nhóm và 15 dòng công bố, kèm ký hiệu †/‡/▾ | `report/tables/e1_main.md`, `e1_full.md` |
| A5 | Tái lập E0 đầy đủ (6 mô hình × 3 bộ, hai cách nhập) | `report/tables/e0_reproduction.md` |
| A6 | Dạng truy vấn và metadata: narrative giúp BM25 (+7,3) và BiLSTM (+7,9), bge gần như không đổi; boost MeSH không giúp mô hình nào | `report/tables/e2_metadata.md` |
| A7 | Nhãn thiếu chi tiết: SciFact-Open 11 hệ thống; TREC-COVID theo vòng 1 → 4 (τ 0,56 → 0,92) | `report/tables/e3_labels.md`, `fig_e3_*` |
| A8 | Chi phí và độ trễ mọi mô hình (p50/p95/p99, USD/1.000 truy vấn) | `report/tables/e4_cost.md` |
| A9 | BiLSTM v1 → v2 và ablation | `report/tables/improvements.md` |
| A10 | Kiểm tra rò rỉ: loại 19 câu train gần trùng (có cặp claim chỉ khác "prevents" và "leads to increased") | `results/data_report/splits.json` |
| A11 | **Trần của reranker (oracle):** với mỗi truy vấn, sắp 100 ứng viên BM25 theo nhãn thật (bài chưa chấm = 0), rồi tính nDCG@10. Kết quả 97,48 / 54,39 / 92,65. Số truy vấn không có bài đúng trong top-100: 0/50, 70/323 (gồm 15 câu BM25 không trả về gì), 21/300 | Tính ngày 11/11 từ `results/runs/<bộ>/test/bm25.trec` và qrels |
| A12 | **Tốc độ BM25 và ngoại suy cả kho:** Pyserini `beir-v1.0.0-trec-covid.flat`, 50 truy vấn, 1 luồng, top-100: p50 16,4 ms, tối đa 69,4 ms. Ngoại suy = p50 đọc 100 bài × 1.713,31 (= 171.331 / 100) | Đo ngày 11/11; `report/tables/e4_cost.md` |

---

## Chuẩn bị hỏi đáp

**1. Reranking khác retrieval thế nào?**
Retrieval phải quét cả kho, nên phải mã hóa tài liệu trước và tra cứu bằng index; mục tiêu là không bỏ sót. Reranking chỉ xử lý k ứng viên, nên được đọc chung câu hỏi và bài; mục tiêu là đúng ở đầu danh sách. Reranker chỉ đổi thứ tự, không thêm bài.

**2. Sao không dùng tìm kiếm bằng vector (dense retrieval) tốt hơn ở tầng một rồi bỏ reranker?**
Dense retrieval giúp tăng recall, nhưng vẫn là bi-encoder: bài được tóm thành một vector trước khi biết câu hỏi. Reranker đọc chung nên xếp đầu danh sách tốt hơn. Seminar giữ BM25 ở tầng một để so được với bảng công bố.

**3. Vì sao chọn k = 100?**
Theo thiết lập chung của RankGPT và Abdallah. k lớn thì trần cao hơn nhưng chi phí tăng tuyến tính. Thí nghiệm k = 10/20/50 đã có trong kế hoạch nhưng chưa chạy với LLM.

**4. Vì sao không dùng LLM để chấm, hoặc chấm tay?**
Để số so được trực tiếp với kết quả đã công bố, và tránh thiên vị. Mọi nhãn đều có sẵn: NIST, chuyên gia, hoặc sinh tự động từ link.

**5. Rốt cuộc reranker nào tốt nhất?**
Luna, Jev và Qwen3 không khác nhau có ý nghĩa thống kê (ngoại lệ: Luna hơn Qwen3 trên NFCorpus). Khác nhau ở chi phí: 1,1 s, 25 s, 29 s mỗi câu hỏi. Chọn theo ngân sách (slide 23).

**6. Listwise hay pointwise tốt hơn?**
Giữa các mô hình khác nhau thì ngang nhau. Muốn trả lời chặt chẽ phải giữ nguyên mô hình và chỉ đổi cách quyết định: Jev pointwise là bước tiếp theo (slide 24).

**7. Jev là hộp đen, sao tin được?**
Nhóm không dựa vào lời quảng cáo; nhóm chỉ đo đầu ra trên nhãn có sẵn, cùng 100 ứng viên như mọi mô hình. Các số của TypeSafe (70–500 ms, RLCD) chỉ trích dẫn kèm nguồn.

**8. BiLSTM thua BM25, trình bày để làm gì?**
Vì chính kết quả âm tính này cho thấy bước nhảy đến từ tiền huấn luyện. Nhóm đã chẩn đoán được nguyên nhân: từ ngoài từ điển, truy vấn quá ngắn, ít dữ liệu học.

**9. Vì sao mọi mô hình đều thấp trên NFCorpus?**
Vì trần chỉ 54,39: 70/323 câu không có bài đúng nào trong 100 ứng viên. Lỗi nằm ở tầng một, reranker không cứu được. Thêm nữa, nhãn sinh tự động và Judged@10 chỉ 30%.

**10. LLM có thể đã thấy dữ liệu test?**
Có thể. Các bộ BEIR công khai từ 2021. Đây là hạn chế; cách kiểm tra là dùng truy vấn ra đời sau thời điểm huấn luyện mô hình.

**11. Vì sao Luna và Jev thấp ở topic 26?**
Chưa phân tích, và đây chỉ là một câu hỏi. Thí nghiệm Jev pointwise sẽ cho biết đó là do cách quyết định hay do mô hình.

**12. Chi phí tính thế nào?**
Mô hình API: chi phí thật từ log token chia cho số truy vấn. Mô hình local: số giây GPU T4 quy ra USD theo giá thuê, nên là ước lượng. Ngoại suy "đọc cả kho" là tuyến tính, chỉ để minh họa độ lớn.

**13. Kết quả bge của nhóm khác bài báo, có sai không?**
Không sai. Nhóm đưa tiêu đề + abstract và được 78,57. Chỉ đưa abstract được 74,26, khớp bài báo (74,79). Nhóm giữ một cách nhập thống nhất và ghi chú điều này.

---

## Bảng tra số nhanh

Đơn vị: nDCG@10 × 100.

| Model | TREC-COVID | NFCorpus | SciFact | TB | Nguồn |
|---|---:|---:|---:|---:|---|
| BM25 | 59,47 | 32,18 | 67,89 | 53,18 | nhóm |
| **Trần (xếp lại hoàn hảo top-100)** | **97,48** | **54,39** | **92,65** | — | nhóm, tính 11/11 |
| LambdaMART | 71,37 | 35,67 | 75,97 | 61,00 | nhóm (3 seed) |
| BiLSTM-ESIM | 55,38 | 26,44 | 72,30 | 51,38 | nhóm (3 seed) |
| BiLSTM-ESIM v2 | 56,54 | 26,73 | 70,15 | 51,14 | nhóm (3 seed) |
| MedCPT-CE | 68,79 | 34,68 | 79,58 | 61,02 | nhóm |
| bge-reranker-base | 68,61 | 31,55 | 71,55 | 57,24 | nhóm |
| bge-reranker-large | 74,23 | 33,83 | 74,20 | 60,75 | nhóm |
| bge-reranker-v2-m3 | 78,57 | 33,69 | 73,99 | 62,08 | nhóm |
| mxbai-rerank-base | 83,06 | 35,48 | 72,03 | 63,52 | nhóm |
| MonoT5-base | 74,08 | 35,06 | 73,24 | 60,79 | nhóm |
| Qwen3-Reranker-4B | 85,00 | 37,37 | 79,35 | 67,24 | nhóm |
| GPT-6 Luna (listwise) | 85,45 | 38,60 | 79,77 | 67,94 | nhóm (đồng đội chạy) |
| Jev (listwise) | 84,41 | 38,24 | 79,14 | 67,27 | nhóm |
| monoBERT | 70,01 | 36,88 | 71,36 | 59,42 | công bố |
| MonoT5-3B | 80,71 | 38,97 | 76,57 | 65,42 | công bố |
| InRanker-3B | 81,75 | 38,25 | 78,31 | 66,10 | công bố |
| Cohere Rerank-v2 | 81,81 | 36,36 | 74,44 | 64,20 | công bố |
| RankGPT gpt-3.5 | 76,67 | 35,62 | 70,43 | 60,91 | công bố |
| RankGPT gpt-4 (top-30) | 85,51 | 38,47 | 74,95 | 66,31 | công bố |
| RankZephyr 7B | 80,70 | 36,58 | 75,13 | 64,14 | công bố |
| ListT5-3B | 84,70 | 37,70 | 77,00 | 66,47 | công bố |
| Setwise Flan-T5-XXL | 76,8 | 34,6 | 75,4 | 62,27 | công bố |

**Tốc độ và chi phí** (p50 cho 100 ứng viên):

| Model | Thời gian | USD / 1.000 truy vấn |
|---|---:|---:|
| BM25 (cả kho, đo 11/11) | 16 ms | 0 |
| BiLSTM | 0,06 s | 0,006 |
| MedCPT | 0,64 s | 0,06 |
| Jev | 1,08 s | 1,62 |
| mxbai | 1,74 s | 0,17 |
| bge-v2-m3 | 2,28 s | 0,22 |
| MonoT5 | 4,32 s | 0,42 |
| Qwen3 | 25,0 s | 2,48 |
| Luna | 28,9 s | 5,61 |

**Thắng/thua so với BM25 trên 50 câu TREC-COVID:**

| Model | Thắng / thua |
|---|---|
| Luna | 45 / 3 |
| Qwen3 | 44 / 3 |
| mxbai | 41 / 6 |
| Jev | 41 / 7 |
| bge-v2-m3 | 40 / 7 |
| MonoT5 | 34 / 14 |
| LambdaMART | 33 / 17 |
| MedCPT | 32 / 16 |
| BiLSTM | 19 / 31 |

---

## Lưu ý trước khi lên trình bày

- **Trọng tâm là reranking.** Khi nói về dữ liệu y sinh, luôn quay về câu hỏi "điều này cho thấy gì về reranker".
- **Số của Jev mới là bảng chính E1**, dùng tiêu chí chung. Chưa có Jev pointwise, tiêu chí y khoa, hay SciFact-Open. Đừng nói vượt quá phạm vi này.
- **Topic 26 chỉ là một câu hỏi**, dùng để minh họa, không dùng để kết luận.
- **Số trong bảng công bố không kiểm định được** so với số của nhóm, vì bài báo không công bố điểm từng truy vấn. Chỉ nói "cao hơn về số", không nói "hơn có ý nghĩa".
- **Mọi con số của TypeSafe** (70–500 ms, giá, RLCD) là số nhà cung cấp công bố. Khi nói luôn kèm "TypeSafe cho biết".
- **Ngoại suy "đọc cả kho" là ước lượng tuyến tính**, chỉ để minh họa độ lớn. Tốc độ BM25 là đo thật.
- **Chi phí của mô hình local là ước lượng** theo giá thuê T4; chi phí API là số thật từ log.
- **Trần và tốc độ BM25 chưa có trong `report/tables/`.** Nếu cần đưa vào báo cáo, nên thêm script tính để tái lập được.
