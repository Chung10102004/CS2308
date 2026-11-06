"""Demo RAG (không đánh giá định lượng): câu hỏi → BM25 (TREC-COVID) → reranker → top-5 → GPT trả lời có trích dẫn.

Chạy: make demo   (hoặc python -m src.demo.rag_app) rồi mở http://127.0.0.1:7860
- BM25 và MedCPT Cross-Encoder (CPU) chạy được không cần key.
- GPT-6 Luna / Jev / phần sinh câu trả lời cần key trong API.json; thiếu key thì app báo, không lỗi.
"""
import asyncio
import functools

import gradio as gr

from ..data import trec_covid
from ..data.beir_loader import doc_text, load_corpus
from ..utils import secrets
from ..utils.io import load_yaml
from ..utils.paths import RESULTS, ensure_java

ensure_java()
DEPTH = 30
RERANKERS = ["BM25 (không rerank)", "MedCPT Cross-Encoder (CPU)", "GPT-6 Luna listwise (cần OpenAI key)", "Jev listwise (cần TypeSafe key)"]


@functools.lru_cache(maxsize=1)
def searcher():
    from pyserini.search.lucene import LuceneSearcher
    return LuceneSearcher.from_prebuilt_index("beir-v1.0.0-trec-covid.flat")


@functools.lru_cache(maxsize=1)
def corpus():
    return load_corpus("trec-covid")


@functools.lru_cache(maxsize=1)
def medcpt():
    import torch
    from transformers import AutoModelForSequenceClassification, AutoTokenizer
    tok = AutoTokenizer.from_pretrained("ncbi/MedCPT-Cross-Encoder")
    m = AutoModelForSequenceClassification.from_pretrained("ncbi/MedCPT-Cross-Encoder").eval()
    torch.set_num_threads(8)
    return tok, m


def rerank_medcpt(q, docs):
    import torch
    tok, m = medcpt()
    with torch.inference_mode():
        enc = tok([q] * len(docs), [doc_text(d) for d in docs], truncation=True, max_length=384, padding=True, return_tensors="pt")
        s = m(**enc).logits.view(-1).tolist()
    return [d for _, d in sorted(zip(s, docs), key=lambda x: -x[0])]


def rerank_gpt(q, docs):
    from ..rerank.gpt_listwise import GPTConfig, GPTListwise
    mcfg = load_yaml("models.yaml")["openai"]["gpt_small"]
    r = GPTListwise(GPTConfig(mcfg["id"], mcfg["reasoning_effort"], len(docs)), "demo", RESULTS / "api_logs" / "demo.jsonl", role="demo")
    order = asyncio.run(r.rerank_query("demo", q, [d["id"] for d in docs], [doc_text(d) for d in docs]))
    by = {d["id"]: d for d in docs}
    return [by[i] for i in order]


def rerank_jev(q, docs):
    from ..rerank.jev import INSTRUCTIONS, JevRanker
    r = JevRanker("demo", RESULTS / "api_logs" / "demo.jsonl")
    s = r.rerank_query("demo", q, [d["id"] for d in docs], [doc_text(d) for d in docs], INSTRUCTIONS["medical"])
    return [d for _, d in sorted(zip(s, docs), key=lambda x: -x[0])]


def answer(q, docs):
    if not secrets.status()["OPENAI_API_KEY"]:
        return "_Chưa điền OPENAI_API_KEY trong API.json — demo chỉ hiện phần truy xuất và rerank._"
    from openai import OpenAI
    m = load_yaml("models.yaml")["openai"]["demo_generator"]
    ctx = "\n\n".join(f"[{d['id']}] {d['title']}\n{d['text'][:1500]}" for d in docs)
    r = OpenAI(api_key=secrets.get("OPENAI_API_KEY")).responses.create(
        model=m["id"], reasoning={"effort": m["reasoning_effort"]},
        input=[{"role": "system", "content": "Answer the biomedical question using ONLY the provided abstracts. Cite every claim with "
                                             "the abstract id in square brackets, e.g. [abc123]. If the abstracts do not answer it, say so."},
               {"role": "user", "content": f"Question: {q}\n\nAbstracts:\n{ctx}"}])
    return r.output_text


def card(rank, d, moved=None):
    arrow = "" if moved is None else (f" ↑{moved}" if moved > 0 else (f" ↓{-moved}" if moved < 0 else " ="))
    return f"**{rank}. {d['title'] or '(không tiêu đề)'}**  `{d['id']}`{arrow}\n\n{d['text'][:280]}…\n"


def run(question, reranker, k):
    question = (question or "").strip()
    if not question:
        return "Nhập một câu hỏi.", "", ""
    hits = searcher().search(question, k=int(k))
    C = corpus()
    docs = [{"id": h.docid, **C[h.docid]} for h in hits if h.docid in C]
    bm_pos = {d["id"]: i for i, d in enumerate(docs)}
    try:
        if reranker.startswith("MedCPT"):
            new = rerank_medcpt(question, docs)
        elif reranker.startswith("GPT"):
            new = rerank_gpt(question, docs)
        elif reranker.startswith("Jev"):
            new = rerank_jev(question, docs)
        else:
            new = docs
    except secrets.MissingKey as e:
        return "\n".join(card(i + 1, d) for i, d in enumerate(docs[:5])), f"_{e}_", ""
    left = "\n".join(card(i + 1, d) for i, d in enumerate(docs[:5]))
    right = "\n".join(card(i + 1, d, bm_pos[d["id"]] - i) for i, d in enumerate(new[:5]))
    try:
        ans = answer(question, new[:5])
    except Exception as e:  # demo: hiện lỗi API thay vì sập app
        ans = f"_Lỗi khi gọi GPT: {type(e).__name__}: {str(e)[:200]}_"
    return left, right, ans


def build():
    examples = [t["question"] for _, t in list(trec_covid.topics(5).items())[:5]]
    with gr.Blocks(title="BioRerank demo") as app:
        gr.Markdown("## BioRerank — demo RAG trên TREC-COVID\nBM25 lấy ứng viên → reranker xếp lại → GPT trả lời từ top-5 (có trích dẫn).")
        with gr.Row():
            q = gr.Textbox(label="Câu hỏi", value=examples[0], scale=4)
            rr = gr.Dropdown(RERANKERS, value=RERANKERS[1], label="Reranker", scale=2)
            k = gr.Slider(10, 100, value=DEPTH, step=10, label="Số ứng viên BM25", scale=1)
        gr.Examples(examples, inputs=q)
        btn = gr.Button("Chạy", variant="primary")
        with gr.Row():
            left = gr.Markdown(label="Top-5 BM25")
            right = gr.Markdown(label="Top-5 sau rerank")
        ans = gr.Markdown(label="Câu trả lời")
        btn.click(run, [q, rr, k], [left, right, ans])
    return app


if __name__ == "__main__":
    build().launch(server_name="127.0.0.1", server_port=7860)
