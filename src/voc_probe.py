"""Probe: run the JCB vocabulary detector over GLOBALISE VOC transcriptions (CC0, 1610-1796).

Input: data/raw/voc/txt/<inventory>.txt (one per VOC inventory number; pages separated by
'#+ NL-HaNA_1.04.02_<inv>_<scan>.xml'). Each page is scored with both signals from jcb_pilot:
  table: short lines pairing a gloss word with a rare word-like token;
  inline: rare word-like token after a naming cue preceded by a gloss word.
Output: data/work/voc/pages.csv  (scan id -> Nationaal Archief page image)
"""
import collections
import csv
import glob
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from jcb_pilot import CUES, GLOSS, TOKEN_RE, clean_token, wordlike_model  # noqa: E402

PAGE_RE = re.compile(r"^#\+ (NL-HaNA_1\.04\.02_\d+_\d+)\.xml$", re.M)
OUT = "data/work/voc"


def pages(path):
    text = open(path, encoding="utf-8").read()
    parts = PAGE_RE.split(text)
    # parts: [preamble, id1, text1, id2, text2, ...]
    for i in range(1, len(parts) - 1, 2):
        yield parts[i], "\n".join(l for l in parts[i + 1].splitlines() if not l.startswith("#+"))


def main(paths):
    os.makedirs(OUT, exist_ok=True)
    allpages = [(pid, t) for p in paths for pid, t in pages(p)]
    df = collections.Counter()
    vol_tokens = collections.defaultdict(set)
    for pid, t in allpages:
        vol_tokens[pid.rsplit("_", 1)[0]].update(f for f in map(clean_token, TOKEN_RE.findall(t)) if f)
    for s in vol_tokens.values():
        df.update(s)
    rare_max = max(2, len(vol_tokens) // 100)
    score, thresh = wordlike_model(df)

    def rare(t):
        return t and t not in GLOSS and df[t] <= rare_max and score(t) >= thresh

    rows = []
    for pid, t in allpages:
        pair, rs, gs = 0, set(), set()
        for line in t.splitlines():
            toks = [x for x in map(clean_token, TOKEN_RE.findall(line)) if x]
            if 2 <= len(toks) <= 5:
                g = [x for x in toks if x in GLOSS]
                r = [x for x in toks if rare(x)]
                if g and r:
                    pair += 1
                    rs.update(r)
                    gs.update(g)
        ts = [clean_token(x) or "" for x in TOKEN_RE.findall(t)]
        inl = set()
        for i in range(len(ts)):
            for c in CUES:
                if ts[i:i + len(c)] == c and any(x in GLOSS for x in ts[max(0, i - 6):i]):
                    for x in ts[i + len(c):i + len(c) + 3]:
                        if rare(x):
                            inl.add(x)
                            break
        tscore = min(len(rs), len(gs)) if pair >= 4 else 0
        if tscore >= 4 or len(inl) >= 2:
            inv, scan = pid.split("_")[-2:]
            rows.append(dict(page=pid, inv=inv, scan=scan, table=tscore, pair_lines=pair, inline=len(inl),
                             forms=" ".join(sorted(rs | inl)[:30]), glosses=" ".join(sorted(gs)[:20])))
    rows.sort(key=lambda r: -(r["table"] + 2 * r["inline"]))
    with open(f"{OUT}/pages.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"{len(allpages)} pages in {len(vol_tokens)} volumes; {len(rows)} flagged "
          f"({sum(r['table'] >= 4 for r in rows)} table, {sum(r['inline'] >= 2 for r in rows)} inline)")


if __name__ == "__main__":
    main(sorted(glob.glob("data/raw/voc/txt/*.txt")))
