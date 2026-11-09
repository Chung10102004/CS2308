"""Build a self-contained, offline HTML presentation from verified local results.

Run: python scripts/build_slides.py. No model API, CDN or web request is used.
"""
import html
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def read(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def esc(value):
    return html.escape(str(value))


def number(value, decimals=2):
    return f"{value:.{decimals}f}".replace(".", ",")


def table(headers, rows, dense=False):
    return '<table class="' + ('dense' if dense else '') + '"><thead><tr>' + ''.join(f'<th scope="col">{esc(x)}</th>' for x in headers) + '</tr></thead><tbody>' + ''.join('<tr' + (' class="highlight"' if r[0] == 'GPT-6 Luna' else '') + '>' + ''.join(f'<td>{esc(x)}</td>' for x in r) + '</tr>' for r in rows) + '</tbody></table>'


def points(items):
    return '<ol class="points">' + ''.join(f'<li><span>{x}</span></li>' for x in items) + '</ol>'


def build():
    e1, e3, e4 = [read(f'results/{s}/{s}.json') for s in ('e1', 'e3', 'e4')]
    cost = read('results/cost_estimates/luna_remaining.json')
    summary = read('results/e1/luna_run_summary.json')
    errors = read('results/error_analysis.json')
    datasets = [('trec-covid', 'TREC-COVID'), ('nfcorpus', 'NFCorpus'), ('scifact', 'SciFact')]
    mean = sum(e1[ds]['R5s']['nDCG@10'] for ds, _ in datasets) / 3
    slides = []

    def slide(title, content, source, note='', cls=''):
        slides.append({'title': title, 'html': f'<section class="slide {cls}" aria-label="{esc(title)}"><h2>{title}</h2><div class="content">{content}</div><p class="source">{source}</p><aside class="notes" hidden>{note or source}</aside></section>'})

    slide('BioRerank', f'<div class="cover-grid"><div><p class="cover-sub">Đánh giá mô hình xếp hạng lại tài liệu<br>trong truy xuất thông tin y sinh</p><p class="cover-line">Cùng BM25 top-100 · Nhãn chuẩn có sẵn<br>GPT-6 Luna là mô hình API duy nhất</p></div><div class="cover-stat"><strong>{number(100*mean)}</strong><span>nDCG@10 trung bình<br>trên ba bộ dữ liệu</span></div></div>', 'Đồ án NLP · Kết quả cập nhật ngày 09/11/2026', 'Nguồn: results/e1/e1.json. Điểm trung bình không đồng nghĩa mô hình thắng mọi truy vấn. Bổ sung thông tin nhóm theo mẫu của môn học.', 'cover')
    slide('Tìm đúng từ khóa chưa đủ để đáp ứng đúng nhu cầu', points(['BM25 tạo ứng viên dựa trên tín hiệu từ vựng; tài liệu đầu có thể lệch trọng tâm câu hỏi.', 'Reranker đọc câu hỏi và tài liệu để <strong>xếp lại cùng tập ứng viên</strong>.', 'Cần đo cả chất lượng, độ phủ nhãn, độ trễ và chi phí.']), 'Nguồn: report/tables/error_cases.md', 'Ví dụ topic 9 TREC-COVID: các bài cùng nhắc COVID và Canada chưa chắc đều trả lời đúng nhu cầu về tác động của đại dịch.')
    slide('Một tập ứng viên chung cho mọi reranker', '<div class="pipeline">' + ''.join(f'<div><b>0{i+1}</b><strong>{name}</strong><span>{desc}</span></div>' for i, (name, desc) in enumerate([('Câu hỏi', 'Từ benchmark'), ('BM25', 'Tối đa 100 ứng viên'), ('Reranker', 'Đổi thứ tự tài liệu'), ('Đánh giá', 'Đối chiếu nhãn chuẩn')])) + '</div><p class="takeaway">GPT là hệ thống được đánh giá.<br>Không dùng GPT để tạo nhãn hay làm người chấm.</p>', 'Nguồn: src/rerank/gpt_listwise.py · src/eval/ir_metrics.py', 'Metric chính là nDCG@10; metric phụ gồm MRR@10 và recall. Candidate set được giữ nguyên, nên recall@100 không thể được reranker cải thiện.')
    slide('Ba bộ chính và một bộ phân tích nhãn thiếu', table(['Bộ dữ liệu', 'Truy vấn', 'Kho tài liệu', 'Vai trò'], [['TREC-COVID', '50', '171.332', 'Câu hỏi COVID-19'], ['NFCorpus', '323', '3.633', 'Truy vấn dinh dưỡng'], ['SciFact', '300', '5.183', 'Mệnh đề khoa học'], ['SciFact-Open', '279', '500.000', 'Phân tích nhãn thiếu']]) + '<p class="small">15 truy vấn NFCorpus không có ứng viên vẫn được tính điểm 0. GPT chưa chạy trên SciFact-Open.</p>', 'Nguồn: report/tables/data_overview.md · dữ liệu BEIR và SciFact-Open')
    slide('Các mô hình đã có kết quả thực nghiệm', table(['Cách tiếp cận', 'Mô hình', 'Thiết lập'], [['Learning-to-rank', 'LambdaMART', 'Huấn luyện, 3 seed'], ['Đối sánh với LSTM', 'BiLSTM-ESIM', 'BioWordVec, 3 seed'], ['Cross-encoder', 'MedCPT-CE, BGE', 'Zero-shot'], ['LLM mã nguồn mở', 'Qwen3-Reranker-4B', 'Kaggle, 2 GPU T4'], ['LLM qua API', 'GPT-6 Luna', 'Listwise, effort none']]), 'Nguồn: src/eval/systems.py · results/e1/e1.json', 'Jev và GPT lớn đã được loại khỏi phạm vi thực hiện. Các mô hình local vẫn là đối chứng; chỉ mô hình API bị giới hạn là GPT-6 Luna.')
    slide('BiLSTM-ESIM là thành phần LSTM của đồ án', '<div class="architecture">BioWordVec 200 chiều <span>→</span> BiLSTM mã hóa <span>→</span> Căn chỉnh mềm <span>→</span> BiLSTM tổng hợp <span>→</span> Điểm liên quan</div>' + table(['BiLSTM v1', 'TREC-COVID', 'NFCorpus', 'SciFact'], [['nDCG@10 × 100', '55,38', '26,44', '72,30']]) + '<p class="takeaway compact">Hơn BM25 ở SciFact, kém trên hai bộ còn lại.</p><p class="small">Hai ablation v2 mới có 1 seed mỗi bản; kết quả chỉ có tính thăm dò.</p>', 'Nguồn: src/kaggle_tasks/bilstm.py · report/tables/improvements.md', 'Bản v1 và v2 đầy đủ có 3 seed. Chưa có embedding/checkpoint và quyền truy cập Kaggle cần để chạy bổ sung hai ablation; không tự tạo kết quả cho seed còn thiếu.')
    slide('Tái lập baseline và ghi rõ sai khác thiết lập', table(['BM25', 'Nhóm', 'Công bố', 'Chênh lệch'], [['TREC-COVID', '59,47', '59,47', '0,00'], ['NFCorpus', '32,18', '30,75', '+1,43'], ['SciFact', '67,89', '67,89', '0,00']]) + '<p class="takeaway compact">NFCorpus ưu tiên so mức tăng so với BM25.</p><p class="small">Cách đưa tiêu đề/abstract và giới hạn token cũng ảnh hưởng so sánh reranker.</p>', 'Nguồn: report/tables/e0_reproduction.md', 'Tránh kết luận vượt một dòng công bố chỉ vì chênh lệch nhỏ. Bảng E0 còn kiểm tra cấu hình tương tự Rankify và mô tả khác biệt.')
    ids = [('R0','BM25'), ('R1','LambdaMART'), ('R2','BiLSTM-ESIM'), ('R3','MedCPT-CE'), ('R4','BGE-v2-m3'), ('R7','Qwen3-Reranker-4B'), ('R5s','GPT-6 Luna')]
    rows = []
    for sid, label in ids:
        vals = [e1[ds][sid]['nDCG@10'] for ds, _ in datasets]
        rows.append([label] + [number(100*v) for v in vals] + [number(100*sum(vals)/3)])
    slide(f'GPT-6 Luna đạt trung bình {number(100*mean)} trên ba bộ', table(['Hệ thống', 'TREC-COVID', 'NFCorpus', 'SciFact', 'TB'], rows, True) + '<p class="small">nDCG@10 × 100. LambdaMART và BiLSTM là trung bình 3 seed; GPT có 1 run.</p>', 'Nguồn: results/e1/e1.json · report/tables/e1_main.md', 'GPT hơn BM25 và BGE-v2-m3 có ý nghĩa sau hiệu chỉnh Holm. Chênh lệch với Qwen3 chưa được kiểm định riêng, nên không nói GPT vượt trội một cách có ý nghĩa.')
    bars = []
    for ds, name in datasets:
        base, luna = [100*e1[ds][sid]['nDCG@10'] for sid in ('R0','R5s')]
        bars.append(f'<div class="bar-group"><h3>{name}</h3><div class="bar-row"><span>BM25</span><div class="bar-track"><i style="width:{base:.6f}%"></i></div><b>{number(base)}</b></div><div class="bar-row luna"><span>Luna</span><div class="bar-track"><i style="width:{luna:.6f}%"></i></div><b>{number(luna)}</b></div><p class="delta">+{number(luna-base)} điểm</p></div>')
    slide('Mức tăng của GPT khác nhau theo bộ dữ liệu', '<div class="bar-chart">' + ''.join(bars) + '</div><p class="small">Chiều dài thanh dùng cùng thang 0–100. Paired bootstrap 10.000 lần và hiệu chỉnh Holm.</p>', 'Nguồn: results/e1/e1.json', 'Ba mức tăng đều có ý nghĩa so với BM25. Không dùng một truy vấn hoặc một bộ để thay thế kết luận tổng thể.')
    slide('Metadata giúp một số mô hình local', table(['Reranker', 'Câu hỏi', 'Từ khóa', 'Câu hỏi + metadata'], [['MedCPT-CE', '68,79', '75,43', '72,08'], ['BGE-v2-m3', '78,57', '78,17', '78,52'], ['BiLSTM-ESIM', '55,38', '51,07', '55,04']]) + '<p class="takeaway compact">Lợi ích phụ thuộc mô hình và cách diễn đạt truy vấn.</p><p class="small">Chưa chạy các biến thể GPT về metadata, tiêu chí hoặc xáo thứ tự.</p>', 'Nguồn: results/e2/e2.json · report/tables/e2_metadata.md', 'Ứng viên BM25 Q-q được giữ cố định cho các reranker. Không suy ra tác động metadata lên GPT từ E1.')
    levels = e3['trec_covid_rounds']['levels']
    so = e3['scifact_open']['intersection']['kendall']
    label_rows = [[str(int(float(k))), number(v['kendall']['tau']), number(v['kendall_condensed']['tau'])] for k,v in levels.items()]
    slide('Nhãn thiếu có thể đổi thứ hạng hệ thống', '<div class="two-col labels-layout"><div><h3>TREC-COVID · 12 hệ thống</h3>' + table(['Nhãn tới vòng', 'Kendall τ', 'τ condensed'], label_rows, True) + '</div><div class="side-stat"><h3>SciFact-Open</h3><strong>' + str(so['swapped_pairs']) + '</strong><p>cặp hệ thống đảo thứ tự</p><p class="small">190 claim chung · 11 hệ thống local<br>Kendall τ = ' + number(so['tau']) + '</p></div></div><p class="small">TREC-COVID đã bổ sung GPT từ run E1 có sẵn, không gọi API mới.</p>', 'Nguồn: results/e3/e3.json · report/tables/e3_labels.md', 'Kendall đo độ tương đồng của thứ hạng hệ thống giữa hai bộ nhãn, không phải mức tương đồng từng tài liệu. GPT chưa có run SciFact-Open.')
    slide('Tăng điểm trung bình không bảo đảm mọi câu tốt hơn', '<div class="case-note"><span class="case-tag">CA TỐT · TOPIC 9</span><h3>Tác động COVID-19 tại Canada</h3><p>Tăng <strong>64,2 điểm</strong> nDCG@10. Bài đầu chuyển từ nhãn 0 sang tài liệu có nhãn liên quan về gánh nặng COVID tại Canada.</p></div><div class="case-note"><span class="case-tag">CA GIẢM ĐIỂM · TOPIC 47</span><h3>Kết cục sức khỏe ở trẻ em</h3><p>Giảm <strong>7,5 điểm</strong>; bài đầu mới chưa có nhãn. Điều này chưa đủ để kết luận tài liệu không liên quan.</p></div>', 'Nguồn: results/error_analysis.json · report/tables/error_cases.md', 'Không chấm thêm tài liệu. Đánh giá một tài liệu chưa có nhãn là sai sẽ làm lẫn phân tích định tính với tạo nhãn mới.')
    cost_names = [('R3','MedCPT-CE'), ('X3','mxbai-base'), ('R7','Qwen3-4B'), ('R5s','GPT-6 Luna')]
    cost_rows = [[name, number(100*e4[sid]['mean_ndcg10_beir3']), number(e4[sid]['p50_ms']/1000) + ' s', number(e4[sid]['usd_per_1k'],3)] for sid,name in cost_names]
    slide('Chất lượng cao hơn đi kèm chi phí và độ trễ', '<div class="inline-stats"><div><strong>' + number(summary['total_cost_usd']) + ' USD</strong><span>chi phí token E1</span></div><div><strong>673</strong><span>truy vấn</span></div><div><strong>5.182</strong><span>lượt gọi API</span></div></div>' + table(['Mô hình', 'TB nDCG@10', 'p50 / câu', 'USD / 1.000 câu'], cost_rows, True), 'Nguồn: results/e4/e4.json · results/api_logs/gpt_small__*.jsonl', 'Giá local quy đổi từ giá thuê T4; API tính theo token log. p50 là tổng thời gian các cửa sổ tuần tự cho một truy vấn, không phải thời gian toàn bộ job chạy song song. Không tính vài lệnh kiểm tra kết nối rất nhỏ.')
    from src.demo.offline_app import demo_result
    cases = [demo_result('trec-covid', q) for q in ('9','6','47')]
    # Slides display titles and labels only; keep raw abstracts out of Git.
    for case in cases:
        for side in ('before', 'after'):
            for doc in case[side]:
                doc.pop('excerpt', None)
    slide('Demo phát lại kết quả đã kiểm chứng', '<div class="demo-toolbar"><label for="case-choice">Chọn ví dụ</label><select id="case-choice"><option value="0">Canada · ca tăng điểm</option><option value="1">Xét nghiệm nhanh · ca tăng điểm</option><option value="2">Trẻ em · ca giảm điểm</option></select><span>0 lượt gọi API</span></div><p id="demo-question" class="demo-question"></p><div class="two-col demo-columns"><div><h3>BM25 <small id="demo-before-score"></small></h3><ol id="demo-before"></ol></div><div><h3>GPT-6 Luna <small id="demo-after-score"></small></h3><ol id="demo-after"></ol></div></div>', 'Demo đầy đủ: python -m src.demo.offline_app → http://127.0.0.1:7860', 'Các tên tài liệu, nhãn và điểm trong ví dụ này lấy trực tiếp từ kết quả E1. Chỉ hiển thị 3 tài liệu đầu để vừa slide; metric vẫn là nDCG@10.')
    slide('Giới hạn cần trình bày khi bảo vệ', points(['Nền BM25 NFCorpus lệch công bố; khác biệt tiêu đề/abstract cũng ảnh hưởng so sánh.', 'Nhãn chưa đầy đủ; GPT có thể đã gặp benchmark công khai trong huấn luyện.', 'Hai ablation BiLSTM v2 còn thiếu seed 1/2; embedding, metadata xử lý sẵn và pack huấn luyện gốc chưa đủ.', 'Chưa có kết quả GPT cho metadata, SciFact-Open hoặc cascade/k mới.']), 'Nguồn: report/draft/tieu_luan.md · HUONG_DAN.md', 'Đây là giới hạn của phạm vi hiện tại, không phải kết quả âm của các thí nghiệm chưa chạy.')
    slide('Kết luận và hướng tiếp tục', points([f'GPT-6 Luna đạt trung bình <strong>{number(100*mean)}</strong>; hơn BM25 và BGE trong các kiểm định đã thực hiện.', 'MedCPT-CE và mxbai là lựa chọn local có chi phí quy đổi thấp hơn; BiLSTM cho thấy giới hạn chuyển miền.', 'Độ phủ nhãn có thể thay đổi kết luận: cần báo rõ bộ nhãn và cách tính condensed.', f'Đã chọn không gọi API mới. Phần GPT bổ sung ước tính <strong>{number(cost["experiments_subtotal_usd"])} USD</strong>, chưa được duyệt chạy.']), 'Nguồn: results/e1/e1.json · results/e3/e3.json · results/cost_estimates/luna_remaining.json', 'Ước tính bổ sung chưa tính khoản E1 đã chi và chưa gồm dự phòng; ba lượt metadata còn dùng proxy token. Không phát sinh thêm phí API khi mở slide này.')
    refs = [('Abdallah et al. (2025)', 'How Good are LLM-based Rerankers?', 'https://arxiv.org/abs/2508.16757'), ('Thakur et al. (2021)', 'BEIR', 'https://arxiv.org/abs/2104.08663'), ('Sun et al. (2023)', 'RankGPT', 'https://arxiv.org/abs/2304.09542'), ('Chen et al. (2017)', 'Enhanced LSTM for Natural Language Inference', 'https://arxiv.org/abs/1609.06038'), ('Jin et al. (2023)', 'MedCPT', 'https://arxiv.org/abs/2307.00589'), ('Wadden et al. (2022)', 'SciFact-Open', 'https://arxiv.org/abs/2210.13777')]
    slide('Tài liệu tham khảo chính', '<ol class="references">' + ''.join(f'<li><a href="{url}" target="_blank" rel="noopener">{author}</a><span>{title}</span></li>' for author,title,url in refs) + '</ol>', 'Danh mục đầy đủ và nguồn số liệu: report/draft/tieu_luan.md', 'Các liên kết chỉ được mở khi người trình bày nhấn vào; bản trình chiếu không tự tải dữ liệu bên ngoài.')

    template = (ROOT / 'src/demo/slides_template.html').read_text(encoding='utf-8')
    output = template.replace('<!-- SLIDES -->', '\n'.join(s['html'] for s in slides))
    payload = json.dumps({'titles':[s['title'] for s in slides], 'cases':cases}, ensure_ascii=False).replace('</','<\\/')
    output = output.replace('/* DATA */', 'const DATA = ' + payload + ';')
    destination = ROOT / 'report/slides/BioRerank.html'
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(output, encoding='utf-8')
    print(f'Built {len(slides)} slides: {destination}')


if __name__ == '__main__':
    build()
