# Hướng dẫn BioRerank

Cập nhật 09/11/2026. Chỉ dùng **GPT-6 Luna** cho API. Người dùng đã chọn **không phát sinh thêm phí API** sau E1.

## Demo offline trên Windows

Trong PowerShell tại thư mục project:

```powershell
.\.venv\Scripts\python.exe -X utf8 -m src.demo.offline_app
```

Mở <http://127.0.0.1:7860>. Chọn bộ dữ liệu và câu hỏi đã đánh giá để xem top-5 trước/sau, mức đổi hạng, nhãn chuẩn và nDCG@10. Demo không đọc key, không gọi API và không sinh câu trả lời mới. Dừng bằng Ctrl+C.

Demo phát lại kết quả của 673 truy vấn, không hỗ trợ câu hỏi tự do. Chế độ RAG trực tiếp cũ trong `src/demo/rag_app.py` chưa được kiểm thử đầy đủ trong môi trường hiện tại.

## Kết quả

| Phần | Nơi lưu / trạng thái |
|---|---|
| Mô hình local và GPU | `results/runs/`, `results/kaggle/` |
| GPT-6 Luna E1 | 673 truy vấn, 5.182 lượt gọi; `results/e1/luna_run_summary.json` |
| Chất lượng GPT | 85,45 / 38,60 / 79,77; `report/tables/e1_main.md` |
| Chi phí GPT E1 | 3,7784 USD theo log token, chưa gồm các lệnh thử kết nối rất nhỏ |
| E2 local và baseline GPT | `report/tables/e2_metadata.md` |
| E3 SciFact-Open | 11 hệ thống local; `report/tables/e3_labels.md` |
| E3 TREC-COVID | 12 hệ thống, gồm GPT; tính từ run đã lưu, không gọi lại mô hình |
| Phân tích lỗi | `report/tables/error_cases.md`, `results/error_analysis.json` |
| Tiểu luận | `report/draft/tieu_luan.md`, bản phát hành `report/BioRerank.md` |

Dữ liệu công khai được phục hồi trong `data/raw/`; pack trong `data/kaggle_pack/` chỉ chứa ứng viên cần cho các run đã lưu. Không dùng pack ứng viên để dựng index toàn kho hoặc thay pack huấn luyện gốc.

## Chấm lại không gọi mô hình

```powershell
.\.venv\Scripts\python.exe -X utf8 scripts/run_experiment.py --only e1 e3 e4
.\.venv\Scripts\python.exe -X utf8 scripts/error_analysis.py
.\.venv\Scripts\python.exe -X utf8 -m pytest -q
```

Các bài API dùng client giả. Nếu sandbox chặn thư mục tạm của pytest, chạy trong terminal có quyền ghi thư mục tạm. E2 metadata lịch sử được giữ nguyên; không chạy lại bước MeSH khi metadata xử lý sẵn chưa có.

## Các lượt API bổ sung chưa được duyệt

- E2 GPT: tiêu chí y khoa, biến thể truy vấn/metadata, xáo thứ tự ứng viên.
- E3 GPT trên SciFact-Open. TREC-COVID đã phân tích thêm từ E1.
- E4 GPT: k=10/20/50 và cascade sau BGE.

Ước tính bổ sung khoảng **10,48 USD**, chưa gồm dự phòng; chi tiết trong `results/cost_estimates/luna_remaining.json`. Ba lượt metadata vẫn dùng proxy token. Không cộng lại 3,78 USD của E1. Đây không phải khoản được phép chi.

`scripts/run_api.py` mặc định chỉ chọn `gpt_small` (GPT-6 Luna) và **chỉ ước tính**. Cần `--execute` hoặc `--confirm` để chạy thật; `--max-usd` chặn trước nếu ước tính vượt trần. Không dùng cờ chạy thật khi chưa có quyết định mới của người dùng. M1 báo thiếu dữ liệu nếu metadata chưa có, thay vì chạy abstract-only rồi ghi nhầm là có metadata.

## Tài nguyên còn thiếu để tái huấn luyện đầy đủ

- Metadata TREC-COVID xử lý sẵn: `data/processed/trec-covid/doc_meta.json`, `topic_mesh.json`.
- ID chia train/dev gốc và pack huấn luyện/đặc trưng gốc.
- Embedding BioWordVec/à la carte, checkpoint và quyền truy cập Kaggle GPU. Hai ablation v2 mới có seed 0; chưa có seed 1/2.

Không thay các file này bằng dữ liệu giả. Kết quả lịch sử được giữ nguyên và được ghi rõ nguồn trong báo cáo. Đợt hiện tại chưa tái lập lại toàn bộ quá trình huấn luyện.

`API.json`, `.env` và thư mục dữ liệu gốc được Git bỏ qua. Không gửi key vào chat hoặc đưa vào báo cáo; demo offline không cần key.

## Slide HTML

Mở `report/slides/BioRerank.html` trong trình duyệt. File chứa 17 trang và toàn bộ CSS/JavaScript/dữ liệu ví dụ; không tải CDN hoặc gọi API. Bản trình chiếu đã được kiểm tra qua máy chủ HTTP local. Công cụ xem tự động của phiên này không cho mở giao thức `file://`.

- Phím ←/→, Page Up/Page Down hoặc Space: chuyển trang; Home/End: đầu/cuối.
- O: mục lục; N: ghi chú; F: toàn màn hình (tùy trình duyệt cho phép).
- Trang 14 có ba ví dụ BM25/GPT lấy từ kết quả đã lưu.

Tạo lại HTML khi số liệu thay đổi:

```powershell
.\.venv\Scripts\python.exe -X utf8 scripts/build_slides.py
```

Không cần PowerPoint. Có thể dùng chức năng in của trình duyệt nếu cần bản giấy; CSS đã có chế độ in từng trang.
