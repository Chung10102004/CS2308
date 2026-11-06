"""Cắt BioWordVec (200 chiều, 13,4 GB, định dạng word2vec nhị phân) theo vocab của gói dữ liệu.

Đọc tuần tự thẳng từ HTTP, không lưu file gốc xuống đĩa. Ra: out/emb.npy (float32), out/words.json, out/stats.json
"""
import json
import time

import numpy as np
import requests

from .common import SMOKE, Pack, out_dir

URL = "https://ftp.ncbi.nlm.nih.gov/pub/lu/Suppl/BioSentVec/BioWordVec_PubMed_MIMICIII_d200.vec.bin"


class Stream:
    def __init__(self, url):
        self.r = requests.get(url, stream=True, timeout=120)
        self.r.raise_for_status()
        self.it = self.r.iter_content(chunk_size=1 << 22)
        self.buf, self.pos, self.read_total = b"", 0, 0

    def _fill(self, n):
        while len(self.buf) - self.pos < n:
            chunk = next(self.it)
            self.read_total += len(chunk)
            self.buf = self.buf[self.pos:] + chunk
            self.pos = 0

    def read(self, n):
        self._fill(n)
        b = self.buf[self.pos:self.pos + n]
        self.pos += n
        return b

    def read_until(self, ch: bytes):
        while True:
            i = self.buf.find(ch, self.pos)
            if i >= 0:
                b = self.buf[self.pos:i]
                self.pos = i + 1
                return b
            self._fill(len(self.buf) - self.pos + (1 << 20))


def main():
    pack, out = Pack(), out_dir("biowordvec_cut")
    vocab = (pack.root / "vocab.txt").read_text(encoding="utf-8").split("\n")
    want = {w: i for i, w in enumerate(vocab)}
    s = Stream(URL)
    n_words, dim = map(int, s.read_until(b"\n").split())
    emb = np.zeros((len(vocab), dim), dtype=np.float32)
    found = np.zeros(len(vocab), dtype=bool)
    t0 = time.time()
    limit = 200_000 if SMOKE else n_words
    for k in range(limit):
        w = s.read_until(b" ").lstrip(b"\n").decode("utf-8", errors="ignore")
        vec = s.read(4 * dim)
        for cand in (w, w.lower()):
            i = want.get(cand)
            if i is not None and not found[i]:
                emb[i] = np.frombuffer(vec, dtype=np.float32)
                found[i] = True
                break
        if k % 1_000_000 == 0:
            print(f"{k}/{n_words} từ, {found.sum()} khớp, {s.read_total / 1e9:.1f} GB, {time.time() - t0:.0f}s", flush=True)
    np.save(out / "emb.npy", emb)
    (out / "words.json").write_text(json.dumps(vocab), encoding="utf-8")
    stats = {"bioWordVec_words": n_words, "dim": dim, "vocab": len(vocab), "found": int(found.sum()),
             "coverage": round(float(found.mean()), 4), "smoke": SMOKE, "seconds": round(time.time() - t0)}
    (out / "stats.json").write_text(json.dumps(stats, indent=1))
    np.save(out / "found.npy", found)
    print(stats, flush=True)


if __name__ == "__main__":
    main()
