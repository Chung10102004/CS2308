"""Log mỗi lệnh gọi API (mục 9.5 của plan) và quy ra USD theo configs/pricing.yaml."""
import json
import threading
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from .io import load_yaml


@dataclass
class CallLog:
    run_id: str
    role: str
    model: str
    mode: str
    query_id: str
    n_candidates: int
    input_tokens: int = 0
    output_tokens: int = 0
    n_requests: int = 1
    latency_ms: float = 0.0
    cost_usd: float = 0.0
    cache_hit: bool = False
    status: str = "ok"
    retries: int = 0
    ts: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat(timespec="seconds"))
    cached_input_tokens: int = 0
    reasoning_tokens: int = 0
    estimated: bool = False


class Pricing:
    def __init__(self, cfg=None):
        self.cfg = cfg or load_yaml("pricing.yaml")

    def openai(self, model, input_tokens, output_tokens, cached_input_tokens=0, batch=False):
        p = self.cfg["openai"]["models"].get(model)
        if p is None:
            return None
        usd = ((input_tokens - cached_input_tokens) * p["input"] + cached_input_tokens * p["cached_input"]
               + output_tokens * p["output"]) / 1e6
        return usd * (self.cfg["openai"]["batch_discount"] if batch else 1.0)

    def jev(self, input_tokens):
        j = self.cfg["jev"]
        return input_tokens * j["input"] / 1e6

    @property
    def confirm_above(self):
        return float(self.cfg["guard"]["confirm_above_usd"])


class CostLogger:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()

    def log(self, rec: CallLog):
        with self._lock, open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(rec), ensure_ascii=False) + "\n")

    def summary(self):
        tot = {"calls": 0, "cache_hits": 0, "requests": 0, "input_tokens": 0, "output_tokens": 0, "usd": 0.0}
        if not self.path.exists():
            return tot
        for line in self.path.read_text(encoding="utf-8").splitlines():
            r = json.loads(line)
            tot["calls"] += 1
            tot["cache_hits"] += int(r["cache_hit"])
            if not r["cache_hit"]:
                tot["requests"] += r["n_requests"]
                tot["input_tokens"] += r["input_tokens"]
                tot["output_tokens"] += r["output_tokens"]
                tot["usd"] += r["cost_usd"]
        return tot
