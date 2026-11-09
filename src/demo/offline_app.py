"""Replay saved BM25/Luna results locally. No model API, key, Java or GPU required.

Run: python -m src.demo.offline_app, then open http://127.0.0.1:7860.
"""
import argparse
import functools
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit

from ..kaggle_tasks.common import Pack
from ..utils.io import ranking, read_json, read_run
from ..utils.paths import PACK, RESULTS, RUNS

DATASETS = {"trec-covid": "TREC-COVID", "nfcorpus": "NFCorpus", "scifact": "SciFact"}


@functools.lru_cache(maxsize=3)
def dataset_data(ds):
    if ds not in DATASETS:
        raise ValueError("Unknown dataset")
    pack = Pack(PACK)
    return {"queries": pack.queries(ds, "test"), "corpus": pack.corpus(ds), "qrels": pack.qrels(ds, "test"),
            "before": read_run(RUNS / ds / "test/bm25.trec"), "after": read_run(RUNS / ds / "test/gpt_small.trec"),
            "scores": read_json(RESULTS / "e1/e1_per_query.json")[ds]}


def demo_result(ds, qid):
    data = dataset_data(ds)
    if qid not in data["queries"]:
        raise ValueError("Unknown query")
    before = ranking(data["before"].get(qid, {}))
    after = ranking(data["after"].get(qid, {}))
    positions = {did: i for i, did in enumerate(before)}
    def cards(ids):
        out = []
        for i, did in enumerate(ids[:5]):
            doc = data["corpus"][did]
            out.append({"id": did, "rank": i + 1, "title": doc.get("title") or "Không có tiêu đề",
                        "excerpt": doc.get("text", "")[:550], "relevance": data["qrels"].get(qid, {}).get(did),
                        "movement": positions.get(did, i) - i})
        return out
    return {"dataset": ds, "qid": qid, "question": data["queries"][qid], "before": cards(before), "after": cards(after),
            "scores": {"before": data["scores"]["R0"].get(qid, 0), "after": data["scores"]["R5s"].get(qid, 0)}, "api_calls": 0}


HTML = r'''<!doctype html><html lang="vi"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>BioRerank — demo kết quả đã lưu</title><style>
:root{--ink:#12263a;--muted:#536779;--line:#dce4eb;--accent:#087e8b;--bg:#f3f6f9}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.5 'Segoe UI',Arial,sans-serif}main{max-width:1280px;margin:auto;padding:32px 28px}header{display:flex;justify-content:space-between;align-items:flex-start;gap:24px}h1{font-size:36px;letter-spacing:-1px;margin:0}h2{font-size:21px;margin:0}p{margin:8px 0;color:var(--muted)}.badge{background:#dbf0ed;color:#146355;padding:7px 12px;border-radius:5px;font-size:13px;white-space:nowrap}.intro{max-width:820px}.controls{margin:26px 0 20px;padding:20px;background:#fff;border:1px solid var(--line);display:grid;grid-template-columns:190px 1fr;gap:18px;border-radius:8px}label{display:block;font-weight:600;font-size:14px;margin-bottom:7px}select{width:100%;padding:11px;border:1px solid #bac8d3;border-radius:4px;background:white;font:inherit;color:var(--ink)}.question{background:#e7f1f4;border-left:4px solid var(--accent);padding:16px 20px;margin-bottom:22px}.question small{color:var(--muted)}.question p{color:var(--ink);font-size:19px;margin:5px 0}.columns{display:grid;grid-template-columns:1fr 1fr;gap:24px}.column-head{display:flex;align-items:center;justify-content:space-between;border-bottom:2px solid #c2ced8;padding-bottom:12px;margin-bottom:14px}.column-head.luna{border-color:var(--accent)}.metric{font-weight:600;font-size:14px;color:var(--muted)}article{border:1px solid var(--line);border-radius:6px;background:white;padding:17px 18px;margin-bottom:12px}article h3{font-size:16px;line-height:1.35;margin:9px 0;color:var(--ink)}article p{font-size:14px;margin:0 0 10px}.meta{display:flex;justify-content:space-between;align-items:center;gap:10px;font-size:12px;color:var(--muted)}.label{padding:3px 7px;border-radius:3px;background:#edf1f4}.label.yes{background:#dff2e9;color:#1b624a}.label.no{background:#fbe9e6;color:#a53a2b}.move{font-weight:600;color:var(--accent)}footer{margin-top:26px;padding:17px 0;border-top:1px solid var(--line);font-size:13px;color:var(--muted)}.empty{padding:24px;background:#fff;border:1px solid var(--line);color:var(--muted)}#error{color:#a32720}a{color:var(--accent)}@media(max-width:760px){main{padding:22px 16px}.columns,.controls{grid-template-columns:1fr}header{display:block}.badge{display:inline-block;margin-top:12px}h1{font-size:30px}}
</style><main><header><div><h1>BioRerank</h1><p class="intro">Xem cách GPT-6 Luna xếp hạng lại tài liệu y sinh so với BM25 trên cùng danh sách ứng viên.</p></div><span class="badge">Kết quả đã lưu · 0 lượt gọi API</span></header>
<section class="controls"><div><label for="dataset">Bộ dữ liệu</label><select id="dataset"><option value="trec-covid">TREC-COVID</option><option value="nfcorpus">NFCorpus</option><option value="scifact">SciFact</option></select></div><div><label for="query">Chọn câu hỏi đã đánh giá</label><select id="query"></select></div></section>
<div id="error" role="alert"></div><section class="question"><small id="qid"></small><p id="question">Đang tải kết quả…</p></section>
<section class="columns"><div><div class="column-head"><h2>Trước · BM25</h2><span id="metric-before" class="metric"></span></div><div id="before"></div></div><div><div class="column-head luna"><h2>Sau · GPT-6 Luna</h2><span id="metric-after" class="metric"></span></div><div id="after"></div></div></section>
<footer>Demo phát lại kết quả E1 đã chạy trên 673 truy vấn. Không gọi API và không sinh câu trả lời mới. Mỗi cột hiển thị 5 tài liệu đầu; điểm nDCG@10 được tính trên 10 tài liệu đầu. Nhãn chuẩn lấy từ benchmark; “chưa có nhãn” không đồng nghĩa với không liên quan.</footer></main>
<script>
const el=id=>document.getElementById(id);async function get(url){const r=await fetch(url);const v=await r.json();if(!r.ok)throw Error(v.error||'Không đọc được dữ liệu');return v;}
function cards(where,rows,luna){el(where).replaceChildren();if(!rows.length){const p=document.createElement('p');p.className='empty';p.textContent='BM25 không tìm thấy ứng viên cho câu hỏi này. Điểm đánh giá được tính bằng 0.';el(where).append(p);return;}
rows.forEach(d=>{const c=document.createElement('article'),m=document.createElement('div'),rank=document.createElement('span'),label=document.createElement('span'),h=document.createElement('h3'),p=document.createElement('p'),b=document.createElement('div'),id=document.createElement('span'),move=document.createElement('span');m.className=b.className='meta';rank.textContent='Hạng '+d.rank;label.className='label'+(d.relevance===null?'':d.relevance>0?' yes':' no');label.textContent=d.relevance===null?'Chưa có nhãn':'Nhãn chuẩn: '+d.relevance;m.append(rank,label);h.textContent=d.title;p.textContent=d.excerpt+(d.excerpt.length>=550?'…':'');id.textContent=d.id;move.className='move';move.textContent=luna?(d.movement>0?'↑ '+d.movement+' bậc':d.movement<0?'↓ '+(-d.movement)+' bậc':'Giữ hạng'):'';b.append(id,move);c.append(m,h,p,b);el(where).append(c);});}
async function result(){try{el('error').textContent='';const d=await get('/api/result?dataset='+encodeURIComponent(el('dataset').value)+'&qid='+encodeURIComponent(el('query').value));el('question').textContent=d.question;el('qid').textContent='Truy vấn '+d.qid+' · '+el('dataset').selectedOptions[0].textContent;for(const k of ['before','after'])el('metric-'+k).textContent='nDCG@10: '+(100*d.scores[k]).toFixed(2);cards('before',d.before,false);cards('after',d.after,true);}catch(e){el('error').textContent=e.message;}}
async function queries(){try{const d=await get('/api/queries?dataset='+encodeURIComponent(el('dataset').value));el('query').replaceChildren(...d.map(q=>{const o=document.createElement('option');o.value=q.id;o.textContent=q.id+' · '+q.text;return o;}));if(el('dataset').value==='trec-covid'&&d.some(q=>q.id==='9'))el('query').value='9';await result();}catch(e){el('error').textContent=e.message;}}
el('dataset').onchange=queries;el('query').onchange=result;queries();
</script></html>'''


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        url = urlsplit(self.path)
        try:
            if url.path == "/":
                self._send(200, HTML.encode("utf-8"), "text/html; charset=utf-8")
                return
            params = parse_qs(url.query)
            ds = params.get("dataset", ["trec-covid"])[0]
            if url.path == "/api/queries":
                data = [{"id": q, "text": text} for q, text in dataset_data(ds)["queries"].items()]
            elif url.path == "/api/result":
                data = demo_result(ds, params.get("qid", [""])[0])
            else:
                self._json(404, {"error": "Not found"})
                return
            self._json(200, data)
        except (ValueError, KeyError) as error:
            self._json(400, {"error": str(error)})
        except FileNotFoundError:
            self._json(503, {"error": "Thiếu dữ liệu hoặc kết quả đã lưu. Xem HUONG_DAN.md."})

    def _json(self, status, data):
        self._send(status, json.dumps(data, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")

    def _send(self, status, body, content_type):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=7860)
    args = parser.parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"BioRerank offline demo: http://127.0.0.1:{args.port} (no model API calls)", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
