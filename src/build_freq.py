"""Corpus-wide token document-frequency and count table over all EEBO-TCP texts.

A token that is rare across the whole corpus (English, Latin, French, Welsh ... texts
alike) is a candidate non-European form. Output: data/work/token_freq.parquet
"""
import glob
import collections
from concurrent.futures import ProcessPoolExecutor

import polars as pl

from glosses import TOKEN_RE

PARTS = sorted(glob.glob("data/raw/eebo/data/*.parquet"))


def count_part(path):
    cnt = collections.Counter()
    df_ = collections.Counter()
    for text in pl.read_parquet(path, columns=["text"])["text"]:
        toks = [t.lower() for t in TOKEN_RE.findall(text)]
        cnt.update(toks)
        df_.update(set(toks))
    return cnt, df_


if __name__ == "__main__":
    tot, docf = collections.Counter(), collections.Counter()
    with ProcessPoolExecutor(12) as ex:
        for c, d in ex.map(count_part, PARTS):
            tot.update(c)
            docf.update(d)
    out = pl.DataFrame({"token": list(tot), "count": list(tot.values()),
                        "docs": [docf[t] for t in tot]})
    out.write_parquet("data/work/token_freq.parquet")
    print(out.height, "types")
