# Hướng dẫn chạy BioRerank

Mọi lệnh chạy trong thư mục `DOAN/`. Plan đầy đủ của đồ án nằm ở `NLP_PROJECT_PLAN.md`.

## Đã làm sẵn (không cần bạn làm gì)

| Phần | Trạng thái | Kết quả nằm ở |
|---|---|---|
| Môi trường `.venv`, thư viện đã ghim phiên bản | xong | `requirements.txt` |
| Tải dữ liệu, chia tập, kiểm rò rỉ | xong | `data/`, `results/data_report/` |
| BM25 top-100 (R0), E0 phần BM25 | xong | `results/runs/`, `results/e0/` |
| Metadata TREC-COVID (CORD-19 + PubMed) | xong | `data/processed/trec-covid/` |
| Phân tích ngữ liệu | xong | `report/figures/fig_data_*.png`, `results/data_report/corpus_stats.json` |
| Reranker GPU trên Kaggle: R2 BiLSTM-ESIM, R3 MedCPT-CE, R4 bge-v2-m3, 4 reranker phụ | xem `report/tables/` | `results/kaggle/`, `results/runs/` |
| R1 LambdaMART | xong | `results/runs/*/test/lambdamart_*.trec` |
| Bảng, hình, demo, nháp tiểu luận | xong phần không cần API | `report/` |
| Code R5 (GPT) và R6 (Jev), có test bằng client giả | xong, **chưa chạy thật** | `src/rerank/gpt_listwise.py`, `src/rerank/jev.py` |

## Việc của bạn: 4 bước

### 1. Điền key vào `API.json`

```json
{
  "OPENAI_API_KEY": "sk-...",
  "TYPESAFE_API_KEY": "...",
  "NCBI_API_KEY": "",
  "NCBI_EMAIL": ""
}
```

- Hai key đầu là bắt buộc. Hai key NCBI không bắt buộc.
- `API.json` đã nằm trong `.gitignore` nên không bị commit.

### 2. Kiểm tra key

```bash
make check-api
```

Lệnh này làm ba việc:

- báo key nào còn thiếu;
- xác nhận các model `gpt-6-luna` và `gpt-6.1-sol` (khai trong `configs/models.yaml`) dùng được với key của bạn;
- gọi thử Jev một lần (chi phí không đáng kể).

Muốn kiểm Jev kỹ hơn trên NanoHotpotQA (kỳ vọng nDCG@10 ≈ 0,969) thì chạy `.venv/bin/python scripts/check_api.py --jev-nano`.

### 3. Xem ước tính chi phí rồi quyết định

```bash
make api-dry                 # đầy đủ, ước tính khoảng 41 USD
make api-dry SKIP_LARGE=1    # bỏ GPT-6.1 Sol, ước tính khoảng 19 USD
```

Bảng in ra liệt kê từng run: số lệnh gọi, số lệnh đã có trong cache, USD.

- Phần đắt nhất là `gpt_large` (GPT-6.1 Sol) ở E1, khoảng 22 USD.
- Nếu bỏ phần này, bảng chính sẽ không có dòng đối ứng với RankGPT gpt-4. Mọi phần khác giữ nguyên.

Giá lấy từ trang chính thức ngày 06/11/2026 và nằm trong `configs/pricing.yaml`. Giá Jev mới lấy từ nguồn thứ cấp, cần đối chiếu trên trang TypeSafe.

### 4. Chạy

```bash
make api-run CONFIRM=1                 # đầy đủ
make api-run CONFIRM=1 SKIP_LARGE=1    # bỏ GPT-6.1 Sol
```

- Nếu tổng ước tính trên 5 USD mà không có `CONFIRM=1` thì lệnh sẽ dừng.
- Mọi lệnh gọi đều được cache trong `data/cache/*.sqlite`. Nếu bị ngắt giữa chừng, chạy lại sẽ tiếp tục từ chỗ dừng và không tính tiền lần hai.
- Chạy xong, lệnh tự chấm lại và sinh lại toàn bộ bảng (`report/tables/`) và hình (`report/figures/`).
- Chi phí thật của từng run được ghi trong `results/api_logs/*.jsonl`. Nên đối chiếu với dashboard thanh toán.

## Lệnh khác

| Lệnh | Việc |
|---|---|
| `make demo` | Demo RAG tại http://127.0.0.1:7860. BM25 và MedCPT chạy không cần key; GPT và Jev cần key |
| `make report` | Chấm lại mọi run và sinh lại bảng, hình |
| `make test` | Unit test, không tốn tiền |
| `make kaggle-run` | Chạy lại các task GPU trên Kaggle (dùng tài khoản Kaggle đã đăng nhập) |
| `make help` | Liệt kê mọi lệnh |

## Bạn vẫn cần tự làm

- Đọc, sửa và chịu trách nhiệm nội dung tiểu luận (`report/draft/`) và slide.
- Kiểm tra quy định của môn về việc dùng công cụ AI.
- Báo deadline.
