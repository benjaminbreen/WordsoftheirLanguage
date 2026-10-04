"""Structural scan of all 4.79M VOC pages for copied word lists (not mentions).

A page scores when many short lines pair a common Dutch gloss word (head, water, fire, one, two...)
with a token that is rare across the archive and word-shaped. Dutch vocabulary and rarity come
from a 1-in-40 sample of pages. Output: data/work/widenet/voc_structural.csv (top pages).
"""
import collections
import csv
import os
import re
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(__file__))
from jcb_pilot import GLOSS_WORDS, fold, wordlike_model  # noqa: E402

DB = "/Users/benbreen/Code/Historical Mysteries/globalise-drugs/data/voc.sqlite"
TOK = re.compile(r"[^\W\d_]{2,}")
DUT = {fold(w) for w in GLOSS_WORDS["dut"].split()} | {fold(w) for w in """
hooft hoofd hayr oogh ogen neus mond tanden tong oor hand handen voet beenen buyk hart vader moeder broeder
suster soon dogter kind sonne maan sterre hemel regen wind vuur water zee rivier aarde steen boom dag nagt
huys dorp boog pijl mes bijl broot rijst visch vleesch hond vogel varken hoen ey melk zout peper
eten drinken slapen komen gaan sien hooren spreken goet quaat groot kleyn wit swart root
een twee drie vier vijf ses seven agt negen tien elf twaalf twintig hondert duysent ja neen""".split()}


def main():
    db = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    df = collections.Counter()
    n = 0
    for (t,) in db.execute("select text from pages where id % 40 = 0"):
        df.update({fold(w) for w in TOK.findall(t)})
        n += 1
    print("sample pages", n, flush=True)
    score_fn, thresh = wordlike_model(df)
    rows = []
    done = 0
    for pid, sid, t in db.execute("select id, scan_id, text from pages"):
        done += 1
        if done % 500000 == 0:
            print(done, len(rows), flush=True)
        lines = t.splitlines()
        if len(lines) < 8:
            continue
        pair, rares, gls = 0, set(), set()
        for l in lines:
            toks = [fold(w) for w in TOK.findall(l)]
            if not 2 <= len(toks) <= 5:
                continue
            g = [x for x in toks if x in DUT]
            r = [x for x in toks if x not in DUT and df[x] <= 1 and 3 <= len(x) <= 14 and score_fn(x) >= thresh]
            if g and r:
                pair += 1
                rares.update(r)
                gls.update(g)
        sc = min(len(rares), len(gls))
        if pair >= 8 and sc >= 6:
            rows.append(dict(scan=sid, score=sc, pair_lines=pair, glosses=" ".join(sorted(gls)[:20]),
                             forms=" ".join(sorted(rares)[:25])))
    rows.sort(key=lambda r: (-r["score"], -r["pair_lines"]))
    os.makedirs("data/work/widenet", exist_ok=True)
    with open("data/work/widenet/voc_structural.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["scan", "score", "pair_lines", "glosses", "forms"])
        w.writeheader()
        w.writerows(rows[:2000])
    print("flagged", len(rows))


if __name__ == "__main__":
    main()
