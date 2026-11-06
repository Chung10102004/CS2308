"""Cache SQLite cho mọi lệnh gọi API: khóa = hash(payload). Chạy dở thì chạy lại không tốn tiền."""
import hashlib
import json
import sqlite3
import threading
from pathlib import Path

from .paths import CACHE


def key_of(payload) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


class Cache:
    def __init__(self, name: str, root: Path = CACHE):
        root.mkdir(parents=True, exist_ok=True)
        self.path = root / f"{name}.sqlite"
        self._lock = threading.Lock()
        self._db = sqlite3.connect(self.path, check_same_thread=False)
        self._db.execute("CREATE TABLE IF NOT EXISTS kv (k TEXT PRIMARY KEY, v TEXT)")
        self._db.commit()

    def get(self, payload):
        k = key_of(payload)
        with self._lock:
            row = self._db.execute("SELECT v FROM kv WHERE k=?", (k,)).fetchone()
        return None if row is None else json.loads(row[0])

    def set(self, payload, value):
        k = key_of(payload)
        with self._lock:
            self._db.execute("INSERT OR REPLACE INTO kv VALUES (?, ?)", (k, json.dumps(value, ensure_ascii=False)))
            self._db.commit()

    def __len__(self):
        with self._lock:
            return self._db.execute("SELECT COUNT(*) FROM kv").fetchone()[0]
