"""Transmission network restricted to confirmed non-European vocabulary windows.

Tokens: rare spellings (in 2..12 texts) that occur inside triage windows judged to be
non-European vocabulary. Edge: two texts share >= MIN_SHARED of these spellings.
Output: data/work/lineage_vocab_edges.parquet
"""
import glob
import json
import collections
import itertools
from concurrent.futures import ProcessPoolExecutor

import polars as pl

from glosses import TOKEN_RE

MIN_SHARED = 4


def vocab_tokens():
    rows = [json.loads(l) for f in sorted(glob.glob("data/work/triage/out_*.jsonl")) + sorted(glob.glob("data/work/triage2/out_*.jsonl"))
            for l in open(f) if l.strip()]
    good = {r["span_id"] for r in rows if r.get("is_vocab") in ("yes", "partial") and not r.get("european_only")
            and not str(r.get("why", "")).startswith("PSEUDO")}
    freq = pl.read_parquet("data/work/token_freq.parquet").filter(
        (pl.col("docs") >= 2) & (pl.col("docs") <= 12) & (pl.col("token").str.len_chars() >= 4))
    rare = set(freq["token"])
    toks = set()
    for f in sorted(glob.glob("data/work/triage/batch_*.jsonl")) + sorted(glob.glob("data/work/triage2/batch_*.jsonl")):
        for l in open(f):
            d = json.loads(l)
            if d["span_id"] in good:
                toks |= {t.lower() for t in TOKEN_RE.findall(d["snippet"])} & rare
    return frozenset(toks)


def scan(args):
    path, toks = args
    out = []
    for tid, text in pl.read_parquet(path, columns=["tcp_id", "text"]).iter_rows():
        hit = {t.lower() for t in TOKEN_RE.findall(text)} & toks
        if hit:
            out.append((tid, hit))
    return out


if __name__ == "__main__":
    toks = vocab_tokens()
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
        for a, b in itertools.combinations(sorted(ds), 2):
            pair[(a, b)].add(t)
    edges = [dict(a=a, b=b, n_shared=len(s), shared=" ".join(sorted(s)))
             for (a, b), s in pair.items() if len(s) >= MIN_SHARED]
    e = pl.DataFrame(edges).sort("n_shared", descending=True)
    e.write_parquet("data/work/lineage_vocab_edges.parquet")
    print(len(toks), "tokens;", e.height, "edges")
