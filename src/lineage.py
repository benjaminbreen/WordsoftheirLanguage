"""Transmission network: which books share clusters of the same rare foreign spellings?

1. Take every rare token (in 2..RARE_DOCS texts) that occurs inside a strong vocabulary
   window (events >= MIN_EVENTS).
2. Scan the whole corpus for the texts containing each such token.
3. Link two texts when they share >= MIN_SHARED of these tokens. Each link keeps the shared
   spellings as evidence, so a researcher can see what was copied.
Output: data/work/lineage_edges.parquet
"""
import glob
import collections
import itertools
from concurrent.futures import ProcessPoolExecutor

import polars as pl

import detect
from glosses import TOKEN_RE

MIN_EVENTS = 12
MIN_SHARED = 6


def window_tokens():
    w = pl.read_parquet("data/work/windows.parquet").filter(pl.col("events") >= MIN_EVENTS)
    freq = pl.read_parquet("data/work/token_freq.parquet").filter(
        (pl.col("docs") >= 2) & (pl.col("docs") <= detect.RARE_DOCS) & (pl.col("token").str.len_chars() >= 4))
    rare = set(freq["token"])
    need = set(w["tcp_id"])
    toks = set()
    for p in sorted(glob.glob("data/raw/eebo/data/*.parquet")):
        df = pl.read_parquet(p, columns=["tcp_id", "text"]).filter(pl.col("tcp_id").is_in(list(need)))
        texts = dict(df.iter_rows())
        for r in w.filter(pl.col("tcp_id").is_in(list(texts))).iter_rows(named=True):
            seg = texts[r["tcp_id"]][r["win_start"]:r["win_start"] + 2800]
            toks |= {t.lower() for t in TOKEN_RE.findall(seg)} & rare
    return toks


def scan(args):
    path, toks = args
    out = []
    for tid, text in pl.read_parquet(path, columns=["tcp_id", "text"]).iter_rows():
        hit = {t.lower() for t in TOKEN_RE.findall(text)} & toks
        if hit:
            out.append((tid, hit))
    return out


if __name__ == "__main__":
    toks = frozenset(window_tokens())
    print(len(toks), "rare vocabulary tokens")
    by_doc = {}
    with ProcessPoolExecutor(12) as ex:
        for res in ex.map(scan, [(p, toks) for p in sorted(glob.glob("data/raw/eebo/data/*.parquet"))]):
            by_doc.update(dict(res))
    inv = collections.defaultdict(set)
    for d, ts in by_doc.items():
        for t in ts:
            inv[t].add(d)
    pair = collections.defaultdict(set)
    for t, ds in inv.items():
        if 2 <= len(ds) <= 8:
            for a, b in itertools.combinations(sorted(ds), 2):
                pair[(a, b)].add(t)
    edges = [dict(a=a, b=b, n_shared=len(s), shared=" ".join(sorted(s)[:60]))
             for (a, b), s in pair.items() if len(s) >= MIN_SHARED]
    e = pl.DataFrame(edges).sort("n_shared", descending=True)
    e.write_parquet("data/work/lineage_edges.parquet")
    print(e.height, "edges")
