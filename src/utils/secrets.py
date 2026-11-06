"""Đọc API key từ API.json (ưu tiên) hoặc biến môi trường. Không bao giờ in giá trị key."""
import json
import os
from pathlib import Path

from .paths import ROOT

API_FILE = Path(os.environ.get("BIORERANK_API_FILE", ROOT / "API.json"))
KNOWN = ("OPENAI_API_KEY", "TYPESAFE_API_KEY", "NCBI_API_KEY", "NCBI_EMAIL")


class MissingKey(RuntimeError):
    pass


def load() -> dict:
    vals = {}
    if API_FILE.exists():
        try:
            vals = json.loads(API_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            raise MissingKey(f"API.json không phải JSON hợp lệ (dòng {e.lineno}). Xem mẫu trong API.example.json.") from e
    out = {}
    for k in KNOWN:
        v = (vals.get(k) or os.environ.get(k) or "").strip()
        out[k] = v
    return out


def get(name: str, required: bool = True) -> str:
    v = load().get(name, "")
    if required and not v:
        raise MissingKey(f"Chưa điền {name} trong API.json ({API_FILE}).")
    return v


def status() -> dict:
    """{tên_key: True/False} — chỉ cho biết đã điền hay chưa."""
    return {k: bool(v) for k, v in load().items()}


def mask(v: str) -> str:
    return "" if not v else f"{v[:3]}…({len(v)} ký tự)"
