"""Character-trigram model of 'European-looking' spellings.

Trained on every token that occurs in >= 50 EEBO-TCP texts: that vocabulary is English,
Latin, French, Italian, Spanish, Dutch, Welsh ... as printed 1473-1700. A rare token with
low average log-probability under this model looks non-European.
"""
import math
import unicodedata
import collections
import functools

import polars as pl


def fold(t: str) -> str:
    t = unicodedata.normalize("NFKD", t.lower())
    return "".join(c for c in t if c.isalpha() and ord(c) < 128)


class TrigramModel:
    def __init__(self, min_docs=50):
        f = pl.read_parquet("data/work/token_freq.parquet").filter(pl.col("docs") >= min_docs)
        tri, bi = collections.Counter(), collections.Counter()
        for tok in f["token"]:
            w = "^^" + fold(tok) + "$"
            for i in range(len(w) - 2):
                tri[w[i:i + 3]] += 1  # type-level counts, so frequent words don't dominate
                bi[w[i:i + 2]] += 1
        self.tri, self.bi = tri, bi
        self.V = 28

    @functools.lru_cache(maxsize=2_000_000)
    def score(self, tok: str) -> float:
        """Mean log-probability per character (higher = more European-looking)."""
        w = "^^" + fold(tok) + "$"
        if len(w) < 5:
            return 0.0
        lp = 0.0
        for i in range(len(w) - 2):
            lp += math.log((self.tri[w[i:i + 3]] + 0.1) / (self.bi[w[i:i + 2]] + 0.1 * self.V))
        return lp / (len(w) - 2)
