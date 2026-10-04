"""Vocabulary-table detector for Evans-TCP and ECCO-TCP (adapted from detect.py).

Raw data: data/raw/{evans,ecco}/data/*.parquet (Vintage-LLM/EVANS and Vintage-LLM/ECCO
on Hugging Face, CC0 TCP transcriptions). Rarity is computed over EEBO + Evans + ECCO combined:
a token is rare if it occurs in <= RARE_DOCS texts across all three corpora and <= RARE_COUNT times.
Scoring reuses detect.scan_text (rare tokens within K of gloss words, plus naming cues).

Output: data/work/widenet/tcp_candidates.parquet (spans) and tcp_texts.parquet (per-text ranking).
"""
import glob
from collections import Counter
from concurrent.futures import ProcessPoolExecutor

import polars as pl

import detect
from glosses import TOKEN_RE

PARTS = sorted(glob.glob("data/raw/evans/data/*.parquet") + glob.glob("data/raw/ecco/data/*.parquet"))


def count_part(path):
    df = pl.read_parquet(path, columns=["text"])
    cnt, docs = Counter(), Counter()
    for text in df["text"]:
        toks = [t.lower() for t in TOKEN_RE.findall(text)]
        cnt.update(toks)
        docs.update(set(toks))
    return cnt, docs


def build_rare():
    cnt, docs = Counter(), Counter()
    with ProcessPoolExecutor(8) as ex:
        for c, d in ex.map(count_part, PARTS):
            cnt.update(c)
            docs.update(d)
    new = pl.DataFrame({"token": list(cnt), "count2": [cnt[t] for t in cnt], "docs2": [docs[t] for t in cnt]})
    old = pl.read_parquet("data/work/token_freq.parquet").select("token", "count", "docs")
    j = new.join(old, on="token", how="left").fill_null(0)
    j = j.with_columns((pl.col("count") + pl.col("count2")).alias("c"), (pl.col("docs") + pl.col("docs2")).alias("d"))
    r = j.filter((pl.col("d") <= detect.RARE_DOCS) & (pl.col("c") <= detect.RARE_COUNT)
                 & (pl.col("token").str.len_chars() >= 3))
    return r["token"].to_list()


def init(rare):
    detect.RARE = frozenset(rare)


def scan_part(path):
    df = pl.read_parquet(path, columns=["tcp_id", "collection", "text"])
    rows = []
    for tid, col, text in zip(df["tcp_id"], df["collection"], df["text"]):
        for r in detect.scan_text(tid, text):
            r["collection"] = col
            rows.append(r)
    return rows


def main_windows():
    rare = build_rare()
    print(len(rare), "rare tokens")
    rows = []
    with ProcessPoolExecutor(8, initializer=init, initargs=(rare,)) as ex:
        for r in ex.map(scan_part, PARTS):
            rows.extend(r)
    out = pl.DataFrame(rows)
    out.write_parquet("data/work/widenet/tcp_candidates.parquet")
    meta = pl.read_parquet(PARTS, columns=["tcp_id", "title", "author", "year"])
    texts = (out.with_columns((pl.col("score") + pl.col("n_cue") + 2 * pl.col("heading").cast(pl.Int64)
                               + pl.col("n_call")).alias("rank"))
             .group_by("tcp_id").agg(pl.col("rank").max(), pl.col("score").max(), pl.len().alias("spans"),
                                     pl.col("collection").first())
             .join(meta, on="tcp_id").sort("rank", descending=True))
    texts.write_parquet("data/work/widenet/tcp_texts.parquet")
    print(out.height, "spans in", texts.height, "texts")


# ---- Second pass: list/table-line detector (more precise for printed vocabularies) ----
# A "pair line" is a short line (markdown list item, table row, or short paragraph line) that
# contains a gloss word and a rare token. Runs of >= MIN_RUN pair lines within GAP lines of each
# other are vocabulary-table candidates.
import re as _re
from glosses import GLOSSES

MIN_RUN = 6
GAP = 3
LINE_SPLIT = _re.compile(r"\n|(?<=\S) - |\|")


def scan_lines(tcp_id, text, rare):
    out, run, last, start = [], [], -99, 0
    pos = 0
    pieces = []
    for m in _re.finditer(r"[^\n]+", text):
        for p in _re.split(r" - |\|| ; ", m.group()):
            p = p.strip(" -*#")
            if p:
                pieces.append((p, m.start()))
    for i, (p, c) in enumerate(pieces):
        # a piece plus its successor (vocabularies are often keyed as alternating lines)
        q = pieces[i + 1][0] if i + 1 < len(pieces) else ""
        if len(p) > 120 or len(q) > 120:
            continue
        tp = [t.lower() for t in TOKEN_RE.findall(p)]
        tq = [t.lower() for t in TOKEN_RE.findall(q)]
        if not (1 <= len(tp) <= 10):
            continue
        toks = tp + tq[:6]
        g = [t for t in toks if t in GLOSSES]
        r = [t for t in toks if t in rare and t not in GLOSSES]
        if g and r:
            if i - last > GAP:
                if len(run) >= MIN_RUN:
                    out.append(run)
                run = []
            run.append((c, g[0], r[0]))
            last = i
    if len(run) >= MIN_RUN:
        out.append(run)
    rows = []
    for run in out:
        rows.append(dict(tcp_id=tcp_id, char_start=run[0][0], char_end=run[-1][0] + 200,
                         n_pairs=len(run), n_gloss=len({x[1] for x in run}),
                         pairs=" ; ".join(f"{a}={b}" for _, a, b in run[:25])))
    return rows


def scan_part_lines(path):
    df = pl.read_parquet(path, columns=["tcp_id", "text"])
    rows = []
    for tid, text in zip(df["tcp_id"], df["text"]):
        rows.extend(scan_lines(tid, text, detect.RARE))
    return rows


def run_lines(rare):
    rows = []
    with ProcessPoolExecutor(8, initializer=init, initargs=(rare,)) as ex:
        for r in ex.map(scan_part_lines, PARTS):
            rows.extend(r)
    df = pl.DataFrame(rows).sort("n_gloss", descending=True)
    df.write_parquet("data/work/widenet/tcp_listspans.parquet")
    print(df.height, "list spans in", df["tcp_id"].n_unique(), "texts")


if __name__ == "__main__":
    import sys
    if "--lines" in sys.argv:
        run_lines(build_rare())
    else:
        main_windows()
