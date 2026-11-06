"""Kiểm tra API.json trước khi chạy thí nghiệm tốn tiền (make check-api).

1. Key nào đã điền / còn thiếu (không in giá trị key).
2. OpenAI: models.list() → các model ID trong configs/models.yaml có tồn tại với key này không; gọi thử 1 lệnh rất nhỏ.
3. Jev: rerank thử 2 tài liệu (tốn < 0,0001 USD).
Thêm --jev-nano để chạy examples/eval.py của jev-reranker trên NanoHotpotQA (kỳ vọng nDCG@10 ≈ 0,969).
"""
import argparse
import asyncio
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.utils import secrets  # noqa: E402
from src.utils.io import load_yaml  # noqa: E402

OK, BAD = "✓", "✗"


def check_keys():
    st = secrets.status()
    print("API.json:", secrets.API_FILE)
    for k, v in st.items():
        need = "bắt buộc" if k in ("OPENAI_API_KEY", "TYPESAFE_API_KEY") else "tùy chọn"
        print(f"  {OK if v else BAD} {k:18s} ({need}){'' if v else ' — CHƯA ĐIỀN'}")
    return st


def check_openai(models):
    from openai import OpenAI
    c = OpenAI(api_key=secrets.get("OPENAI_API_KEY"))
    ids = {m.id for m in c.models.list()}
    good = True
    for role in ("gpt_small", "gpt_large", "demo_generator"):
        mid = models["openai"][role]["id"]
        print(f"  {OK if mid in ids else BAD} {role:15s} {mid}")
        good &= mid in ids
    m = models["openai"]["gpt_small"]
    r = c.responses.create(model=m["id"], input="Reply with the single word: ok", reasoning={"effort": m["reasoning_effort"]},
                           max_output_tokens=16)
    print(f"  {OK} gọi thử {m['id']}: '{r.output_text.strip()[:20]}' ({r.usage.input_tokens} in / {r.usage.output_tokens} out token)")
    return good


def check_jev(models):
    from src.rerank.jev import INSTRUCTIONS, JevRanker
    r = JevRanker("check_api", ROOT / "results" / "api_logs" / "check_api.jsonl", model=models["jev"]["model"])
    sc = r.rerank_query("check", "Which planet is called the Red Planet?", ["a", "b"],
                        ["Venus has a thick atmosphere.", "Mars is known as the Red Planet."], INSTRUCTIONS["generic"])
    good = sc[1] > sc[0]
    print(f"  {OK if good else BAD} Jev rerank thử: điểm {sc[0]:.2f} / {sc[1]:.2f} (bài đúng phải cao hơn)")
    return good


def jev_nano():
    d = ROOT / "data" / "raw" / "jev-reranker"
    if not d.exists():
        subprocess.run(["git", "clone", "--depth", "1", "https://github.com/hotchpotch/jev-reranker", str(d)], check=True)
    print("  chạy examples/eval.py (NanoHotpotQA)…")
    env = {**__import__("os").environ, "TYPESAFE_API_KEY": secrets.get("TYPESAFE_API_KEY")}
    subprocess.run([sys.executable, "examples/eval.py"], cwd=d, env=env, check=False)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jev-nano", action="store_true")
    a = ap.parse_args()
    models = load_yaml("models.yaml")
    st = check_keys()
    ok = True
    if st["OPENAI_API_KEY"]:
        print("OpenAI:")
        try:
            ok &= check_openai(models)
        except Exception as e:
            ok = False
            print(f"  {BAD} lỗi OpenAI: {type(e).__name__}: {str(e)[:200]}")
    else:
        ok = False
    if st["TYPESAFE_API_KEY"]:
        print("Jev:")
        try:
            ok &= check_jev(models)
            if a.jev_nano:
                jev_nano()
        except Exception as e:
            ok = False
            print(f"  {BAD} lỗi Jev: {type(e).__name__}: {str(e)[:200]}")
    else:
        ok = False
    print("\nKẾT QUẢ:", "sẵn sàng — chạy `make api-dry`" if ok else "chưa sẵn sàng — sửa các dòng ✗ ở trên")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
