"""High-recall detector for embedded vocabularies in EEBO-TCP.

Each token is tagged G (a common gloss word such as water, head, knife, one),
R (rare across the whole corpus: candidate foreign form) or O. An "event" is an
R within K tokens of a G. Over a sliding window we count the distinct glosses and
distinct rare forms taking part in events; a vocabulary list scores high on both,
while a passage naming one river or one king does not.

Output: data/work/candidates.parquet, one row per merged candidate span.
"""
import glob
import sys
from concurrent.futures import ProcessPoolExecutor

import polars as pl

from glosses import GLOSSES, STOP, TOKEN_RE, HEADING_RE, CALL_RE

CUES = frozenset("call calls called calleth cal termed terme named name signifieth signifies "
                 "signifying signifie word words tongue language languages".split())

K = 3            # max token distance between a rare form and its gloss
WIN = 400        # window size in tokens
STEP = 100
MIN_SCORE = 4    # min(distinct glosses, distinct rare forms) to keep a window
RARE_DOCS = 8    # a token in <= this many texts counts as rare
RARE_COUNT = 60

RARE: frozenset = frozenset()


def load_rare():
    f = pl.read_parquet("data/work/token_freq.parquet")
    r = f.filter((pl.col("docs") <= RARE_DOCS) & (pl.col("count") <= RARE_COUNT)
                 & (pl.col("token").str.len_chars() >= 3))
    return frozenset(r["token"].to_list())


def init():
    global RARE
    RARE = load_rare()


def scan_text(tcp_id, text):
    toks = [(m.group(), m.start(), m.end()) for m in TOKEN_RE.finditer(text)]
    n = len(toks)
    if n < 20:
        return []
    tags = []
    for t, _, _ in toks:
        lt = t.lower()
        if lt in GLOSSES:
            tags.append("G")
        elif lt in RARE and not lt.isdigit():
            tags.append("R")
        else:
            tags.append("O")
    # events: index of rare token -> set of gloss tokens nearby
    ev_r = {}
    ev_g = {}
    for i, tg in enumerate(tags):
        if tg != "R":
            continue
        for j in range(max(0, i - K), min(n, i + K + 1)):
            if tags[j] == "G":
                ev_r[i] = toks[i][0].lower()
                ev_g[j] = toks[j][0].lower()
    # inline mode: rare form shortly after a naming cue ("they call X", "named X")
    cue_r = {}
    for i, (t, _, _) in enumerate(toks):
        if t.lower() in CUES:
            for j in range(i + 1, min(n, i + 6)):
                if tags[j] == "R":
                    cue_r[j] = toks[j][0].lower()
    if len(ev_r) < MIN_SCORE and len(cue_r) < MIN_SCORE:
        return []
    r_idx = sorted(ev_r)
    g_idx = sorted(ev_g)
    c_idx = sorted(cue_r)
    import bisect
    spans = []
    for s in range(0, max(1, n - WIN // 2), STEP):
        e = s + WIN
        rs = {ev_r[i] for i in r_idx[bisect.bisect_left(r_idx, s):bisect.bisect_left(r_idx, e)]}
        cs = {cue_r[i] for i in c_idx[bisect.bisect_left(c_idx, s):bisect.bisect_left(c_idx, e)]}
        if len(rs) < MIN_SCORE and len(cs) < 3:
            continue
        gs = {ev_g[i] for i in g_idx[bisect.bisect_left(g_idx, s):bisect.bisect_left(g_idx, e)]}
        sc = min(len(rs), len(gs))
        if sc >= MIN_SCORE or len(cs) >= 3:
            spans.append([s, min(e, n) - 1, sc, rs | cs, gs, cs])
    # merge overlapping windows
    merged = []
    for sp in spans:
        if merged and sp[0] <= merged[-1][1]:
            m = merged[-1]
            m[1] = sp[1]
            m[2] = max(m[2], sp[2])
            m[3] |= sp[3]
            m[4] |= sp[4]
            m[5] |= sp[5]
        else:
            merged.append(sp)
    out = []
    for s, e, sc, rs, gs, cs in merged:
        c0, c1 = toks[s][1], toks[e][2]
        seg = text[c0:c1]
        pre = text[max(0, c0 - 1500):c0]
        out.append(dict(
            tcp_id=tcp_id, tok_start=s, tok_end=e, char_start=c0, char_end=c1,
            score=sc, n_cue=len(cs), n_rare=len(rs), n_gloss=len(gs),
            n_call=len(CALL_RE.findall(seg)),
            heading=bool(HEADING_RE.search(pre[-400:] + seg[:300])),
            rare_sample=" ".join(sorted(rs)[:40]),
            gloss_sample=" ".join(sorted(gs)[:40]),
        ))
    return out


def scan_part(path):
    df = pl.read_parquet(path, columns=["tcp_id", "text"])
    rows = []
    for tid, text in zip(df["tcp_id"], df["text"]):
        rows.extend(scan_text(tid, text))
    return rows


if __name__ == "__main__":
    parts = sorted(glob.glob("data/raw/eebo/data/*.parquet"))
    if len(sys.argv) > 1:
        parts = parts[: int(sys.argv[1])]
    rows = []
    with ProcessPoolExecutor(12, initializer=init) as ex:
        for r in ex.map(scan_part, parts):
            rows.extend(r)
    out = pl.DataFrame(rows)
    out.write_parquet("data/work/candidates.parquet")
    print(out.height, "candidate spans in", out["tcp_id"].n_unique(), "texts")
