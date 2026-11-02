"""Busca híbrida: BM25 (lexical) + embedding denso local, fundidos por RRF.

- BM25: implementação própria (k1=1.5, b=0.75), sem dependência.
- Denso: 'hashing embedding' de n-gramas de caracteres (3-5) em vetor esparso
  normalizado + cosseno. Não é um modelo neural, mas captura similaridade de
  subpalavras (ferias~feriado, reembolso~reembolsadas) e roda offline/grátis.
  O contrato (`dense_search`) é o mesmo de um embedding neural; trocar é só
  substituir `_embed`.
- Fusão: Reciprocal Rank Fusion (RRF, k=60), robusta a escalas diferentes de score."""
from __future__ import annotations
import math
import re
import unicodedata
import zlib
from collections import Counter

from .corpus import PASSAGES, Passage

STOP = {"a", "o", "as", "os", "de", "da", "do", "das", "dos", "e", "em", "para", "por",
        "um", "uma", "no", "na", "nos", "nas", "que", "se", "com", "ao", "ou", "qual",
        "quais", "quanto", "quantos", "quantas", "como", "sao", "ser", "tem", "deve"}


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s.lower())
    return "".join(c for c in s if not unicodedata.combining(c))


def tok(s: str) -> list[str]:
    return [t for t in re.findall(r"[a-z0-9]+", norm(s)) if t not in STOP]


def _embed(text: str) -> dict[int, float]:
    # crc32 (e NAO hash()): hash() de str varia a cada execucao (PYTHONHASHSEED) e
    # tornaria o embedding e os numeros do eval nao reproduziveis.
    grams: Counter = Counter()
    for w in tok(text):
        w = f"<{w}>"
        for n in (3, 4, 5):
            for i in range(len(w) - n + 1):
                grams[zlib.crc32(w[i:i + n].encode()) % 4096] += 1
    norm_ = math.sqrt(sum(v * v for v in grams.values())) or 1.0
    return {k: v / norm_ for k, v in grams.items()}


def _cos(a: dict[int, float], b: dict[int, float]) -> float:
    if len(a) > len(b):
        a, b = b, a
    return sum(v * b.get(k, 0.0) for k, v in a.items())


class HybridIndex:
    def __init__(self, passages: list[Passage] | None = None, k1: float = 1.5, b: float = 0.75):
        self.passages = passages or PASSAGES
        self.k1, self.b = k1, b
        self.tf = [Counter(tok(p.text)) for p in self.passages]
        self.len = [sum(t.values()) for t in self.tf]
        self.avg = sum(self.len) / len(self.len)
        df: Counter = Counter()
        for t in self.tf:
            df.update(t.keys())
        n = len(self.passages)
        self.idf = {t: math.log(1 + (n - d + 0.5) / (d + 0.5)) for t, d in df.items()}
        self.vec = [_embed(p.text) for p in self.passages]

    def bm25(self, query: str) -> list[float]:
        q = tok(query)
        out = []
        for i, tf in enumerate(self.tf):
            s = 0.0
            for t in q:
                f = tf.get(t, 0)
                if f:
                    s += self.idf.get(t, 0.0) * f * (self.k1 + 1) / (
                        f + self.k1 * (1 - self.b + self.b * self.len[i] / self.avg))
            out.append(s)
        return out

    def dense(self, query: str) -> list[float]:
        qv = _embed(query)
        return [_cos(qv, v) for v in self.vec]

    @staticmethod
    def _rank(scores: list[float]) -> list[int]:
        return [i for i, s in sorted(enumerate(scores), key=lambda x: -x[1]) if s > 0]

    def search(self, query: str, k: int = 3, mode: str = "hybrid", rrf_k: int = 60) -> list[tuple[Passage, float]]:
        if mode == "bm25":
            sc = self.bm25(query)
            order = self._rank(sc)
            return [(self.passages[i], sc[i]) for i in order[:k]]
        if mode == "dense":
            sc = self.dense(query)
            order = self._rank(sc)
            return [(self.passages[i], sc[i]) for i in order[:k]]
        fused: dict[int, float] = {}
        for sc in (self.bm25(query), self.dense(query)):
            for rank, i in enumerate(self._rank(sc)):
                fused[i] = fused.get(i, 0.0) + 1.0 / (rrf_k + rank + 1)
        top = sorted(fused.items(), key=lambda x: -x[1])[:k]
        return [(self.passages[i], s) for i, s in top]
