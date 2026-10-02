"""Re-find each table in an Internet Archive scan and align its entries to printed lines.

For every table:
  1. fetch the IA item's metadata and page OCR (`_djvu.xml`: words with pixel boxes);
  2. score pages by how many of the table's transcribed forms appear (fuzzy, early-modern folding);
     keep the best contiguous run of pages;
  3. align entries, in order, to OCR words on those pages, and widen each match to its printed line;
  4. download the page images (full resolution, by leaf) and write web sizes.

Output: data/site/scans/<table>.json  and  site/public/scans/<table>/<leaf>-{900,1800}.webp
Entry boxes are fractions of page width/height, so they work at any display size.
"""
import csv
import io
import json
import os
import re
import sys
import unicodedata
from concurrent.futures import ThreadPoolExecutor

import requests
from lxml import etree
from PIL import Image
from rapidfuzz import fuzz

RAW = "data/raw/ia"
OUT_JSON = "data/site/scans"
OUT_IMG = "site/public/scans"
SIZES = (900, 1800)

# table id -> (IA identifier, entries csv, row filter on language label, scan note)
TABLES = {
    "rosier": ("purchaspilgrimes04", "data/work/extract/rosier_A71306", None, ""),
    "wood": ("newenglandsprosp01wood", "data/work/extract/wood_A15685", None, ""),
    "williams": ("keyintolanguageo02will", "data/work/extract/williams_A66450", None, ""),
    "smith": ("mapofvirginiavvi00smit", "data/work/extract/smith_map_A12466", None, ""),
    "cartier": ("shortebriefenarr00cart", "data/work/extract/cartier_A18057", None, ""),
    "rochefort": ("historyofcaribby00roch", "data/work/extract/rochefort_A57484", None, ""),
    "scheffer": ("historyoflapland02sche", "data/work/extract/scheffer_A62332", "lapland", ""),
    "knox": ("gpl_1730637", "data/work/extract/knox_A47586", None, ""),
    "boothby": ("bim_early-english-books-1641-1700_a-breife-discovery-or-de_boothby-richard_1647", "data/work/extract/boothby_A28809", None, "microfilm"),
    "vanneck": ("bim_early-english-books-1475-1640_the-journall-or-dayly-re_neck-jacob-van_1601", "data/work/extract/vanneck_A08052", None, "microfilm"),
    "herbert": ("b30326825", "data/work/extract/herbert_A03065", None, ""),
    "trinidad": ("bim_early-english-books-1475-1640_the-third-and-last-volum_hakluyt-richard_1600_3", "data/work/extract2/trinidad_A02495", None, "microfilm"),
    "burrough": ("b30333635_0001", "data/work/extract2/sami_burrough_A02495", None, ""),
    "pegu": ("bim_early-english-books-1475-1640_a-true-and-large-discour_east-indies_1603", "data/work/extract2/pegu_A21094", None, "microfilm"),
    "greenland": ("voyagestravellso00olea", "data/work/extract2/greenland_olearius_A53322", None, ""),
    "gthomas": ("historicalgeogra01thom", "data/work/extract2/gthomas_A64548", None, ""),
    "chile": ("americabeinglate01mont", "data/work/extract2/chilesian_ogilby_A53222", None, ""),
    "tupi": ("americabeinglate01mont", "data/work/extract2/tupi_ogilby_A53222", None, ""),
    "ludolf": ("bub_gb_buNBAQAAMAAJ", "data/work/extract2/ludolf_gallan_A49450", None, "1684 edition"),
}


def fold(s):
    s = unicodedata.normalize("NFKD", s.lower())
    s = "".join(c for c in s if c.isalpha())
    s = s.replace("ſ", "s").replace("f", "s").replace("v", "u").replace("j", "i").replace("y", "i").replace("w", "uu")
    return s


def meta(ia):
    p = f"{RAW}/{ia}_meta.json"
    if not os.path.exists(p):
        json.dump(requests.get(f"https://archive.org/metadata/{ia}", timeout=60).json(), open(p, "w"))
    return json.load(open(p))


def pages(ia):
    p = f"{RAW}/{ia}_djvu.xml"
    if not os.path.exists(p):
        r = requests.get(f"https://archive.org/download/{ia}/{ia}_djvu.xml", timeout=300)
        r.raise_for_status()
        open(p, "wb").write(r.content)
    out = []
    for o in etree.parse(p).iter("OBJECT"):
        pg = [q.get("value") for q in o.iter("PARAM") if q.get("name") == "PAGE"]
        m = re.search(r"_(\d+)\.djvu", pg[0]) if pg else None
        if not m:
            continue
        words = []
        for w in o.iter("WORD"):
            c = (w.get("coords") or "").split(",")
            if len(c) < 4 or not (w.text or "").strip():
                continue
            l, b, r, t = map(int, c[:4])
            words.append((w.text.strip(), l, t, r, b))
        out.append(dict(leaf=int(m.group(1)), w=int(o.get("width")), h=int(o.get("height")), words=words))
    return out


def entries(path, filt):
    rows = list(csv.DictReader(open(path + ".entries.csv", encoding="utf-8")))
    return [(i + 1, r) for i, r in enumerate(rows)
            if not filt or filt in (r.get("form_language_label_as_printed") or "").lower()]


def key_tokens(form):
    toks = [fold(t) for t in re.split(r"[\s,\-]+", form) if len(fold(t)) >= 3]
    return sorted(toks, key=len, reverse=True)[:2]


def locate(pgs, ents):
    keys = [key_tokens(r["form_as_printed"]) for _, r in ents]
    scores = []
    for p in pgs:
        ws = {fold(w[0]) for w in p["words"] if len(fold(w[0])) >= 3}
        sc = 0
        for ks in keys:
            if ks and any(max((fuzz.ratio(k, w) for w in ws), default=0) >= 86 for k in ks[:1]):
                sc += 1
        scores.append(sc)
    best = max(range(len(pgs)), key=lambda i: scores[i])
    thr = max(2, 0.2 * scores[best])
    lo = hi = best
    while lo - 1 >= 0 and (scores[lo - 1] >= thr or (lo - 2 >= 0 and scores[lo - 2] >= thr)):
        lo -= 1
    while hi + 1 < len(pgs) and (scores[hi + 1] >= thr or (hi + 2 < len(pgs) and scores[hi + 2] >= thr)):
        hi += 1
    while scores[lo] < thr:
        lo += 1
    while scores[hi] < thr:
        hi -= 1
    return list(range(lo, hi + 1)), scores


def segments(p):
    """Group a page's OCR words into printed line segments (split at wide horizontal gaps)."""
    W = sorted(p["words"], key=lambda w: ((w[2] + w[4]) / 2, w[1]))
    if not W:
        return []
    hs = sorted(w[4] - w[2] for w in W)
    mh = hs[len(hs) // 2] or 1
    lines, cur = [], [W[0]]
    for w in W[1:]:
        if abs((w[2] + w[4]) / 2 - (cur[-1][2] + cur[-1][4]) / 2) < 0.36 * mh:
            cur.append(w)
        else:
            lines.append(cur); cur = [w]
    lines.append(cur)
    cys = sorted(sum((w[2] + w[4]) / 2 for w in ln) / len(ln) for ln in lines)
    gaps = sorted(b - a for a, b in zip(cys, cys[1:]) if 0.6 * mh < b - a < 3 * mh)
    pitch = gaps[len(gaps) // 2] if gaps else 1.4 * mh
    segs = []
    for ln in lines:
        ln = sorted(ln, key=lambda w: w[1])
        group = [ln[0]]
        for w in ln[1:]:
            if w[1] - group[-1][3] > 0.045 * p["w"]:
                segs.append(group); group = [w]
            else:
                group.append(w)
        segs.append(group)
    out = []
    for g in segs:
        L, T, R, B = min(w[1] for w in g), min(w[2] for w in g), max(w[3] for w in g), max(w[4] for w in g)
        gcy = sorted((w[2] + w[4]) / 2 for w in g)
        out.append(dict(text=" ".join(w[0] for w in g), box=(L, T, R, B), cy=gcy[len(gcy) // 2], mh=mh, pitch=pitch,
                        col=0 if L < 0.45 * p["w"] else 1))
    out.sort(key=lambda s: (s["col"], s["box"][1]))
    return out


def psim(a, b):
    """Similarity of target a to OCR text b; a short b can never fully 'contain' a long a."""
    if len(a) < 2 or len(b) < 3:
        return 0
    return fuzz.partial_ratio(a, b) if len(b) >= len(a) else fuzz.ratio(a, b)


def units(pgs, idxs, split=None):
    """Candidate printed units: a line segment alone, or a segment plus its right-hand neighbour
    on the same line (form column + gloss column). `split` (fraction of page width) separates two
    text columns; units never cross it and are read column by column."""
    out = []
    for pi in idxs:
        p = pgs[pi]
        X = split * p["w"] if split else None
        segs = segments(p)
        col = lambda b: 0 if X is None or b[0] < X else 1
        for sg in segs:
            L, T, R, B = sg["box"]
            c = col(sg["box"])
            if X is not None and c == 0:
                R = min(R, X)
            out.append(dict(pi=pi, left=fold(sg["text"]), right="", box=(L, T, R, B), cy=sg["cy"], mh=sg["mh"], pitch=sg["pitch"], order=(pi, c, T, L)))
            h = B - T
            nb = [o for o in segs if o is not sg and col(o["box"]) == c and abs(o["cy"] - sg["cy"]) < 0.35 * sg["mh"]
                  and 0 < o["box"][0] - sg["box"][2] < 0.22 * p["w"]]
            if nb:
                o = min(nb, key=lambda o: o["box"][0])
                R2 = min(o["box"][2], X) if (X is not None and c == 0) else o["box"][2]
                out.append(dict(pi=pi, left=fold(sg["text"]), right=fold(o["text"]),
                                box=(L, min(T, o["box"][1]), R2, max(B, o["box"][3])), cy=sg["cy"], mh=sg["mh"], pitch=sg["pitch"],
                                order=(pi, c, T, L + 0.5)))
    out.sort(key=lambda u: u["order"])
    return out


def sim(entry, u):
    f, g = fold(entry["form_as_printed"]), fold(entry["gloss_as_printed"] or "")
    whole = u["left"] + u["right"]
    cands = [(psim(f, whole) + psim(g, whole)) / 2]
    if u["right"]:
        cands.append((psim(f, u["left"]) + psim(g, u["right"])) / 2)
        cands.append((psim(g, u["left"]) + psim(f, u["right"])) / 2)
    sf = psim(f, u["left"])
    if sf >= 86 and len(f) >= 4:
        cands.append(sf * 0.9)
    return max(cands)


def align(pgs, idxs, ents):
    """Try one-column reading and two-column readings at several splits; keep the best."""
    best = None
    for split in [None] + [round(0.30 + 0.025 * k, 3) for k in range(17)]:
        total, boxes = align_once(pgs, idxs, ents, split)
        if best is None or total > best[0] + 1e-6:
            best = (total, boxes, split)
    return best[1]


def align_once(pgs, idxs, ents, split):
    """Order-preserving weighted alignment of entries to printed units (free gaps; several entries
    may share one line, as in run-on lists)."""
    S = units(pgs, idxs, split)
    n, m = len(ents), len(S)
    if not n or not m:
        return 0, {}
    TH = 64
    sc = [[sim(ents[i][1], S[j]) - TH for j in range(m)] for i in range(n)]
    D = [[0.0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        Di, Dp, sci = D[i], D[i - 1], sc[i - 1]
        for j in range(1, m + 1):
            v = sci[j - 1]
            best = Dp[j - 1] + v if v > 0 else Dp[j - 1]
            if v > 0 and Dp[j] + v > best: best = Dp[j] + v
            if Dp[j] > best: best = Dp[j]
            if Di[j - 1] > best: best = Di[j - 1]
            Di[j] = best
    boxes, i, j = {}, n, m
    while i > 0 and j > 0:
        s_ = sc[i - 1][j - 1]
        same_line = s_ > 0 and abs(D[i][j] - (D[i - 1][j] + s_)) < 1e-9
        if s_ > 0 and (abs(D[i][j] - (D[i - 1][j - 1] + s_)) < 1e-9 or same_line):
            u = S[j - 1]
            p = pgs[u["pi"]]
            L, _, R, _ = u["box"]
            mh, pitch = u["mh"], u["pitch"]
            up, down = min(0.72 * mh, 0.56 * pitch), min(0.62 * mh, 0.46 * pitch)
            T, B = u["cy"] - up, u["cy"] + down
            pad = 0.3 * mh
            fform = fold(ents[i - 1][1]["form_as_printed"])
            fs = max(psim(fform, u["left"]), psim(fform, u["left"] + u["right"]))
            boxes[ents[i - 1][0]] = dict(page=idxs.index(u["pi"]), score=round(s_ + TH), form_score=round(fs),
                box=[round(max(0, (L - pad) / p["w"]), 4), round(max(0, T / p["h"]), 4),
                     round(min(1, (R - L + 2 * pad) / p["w"]), 4), round(min(1, (B - T) / p["h"]), 4)])
            i -= 1
            if not same_line:
                j -= 1
        elif D[i][j] == D[i - 1][j]:
            i -= 1
        else:
            j -= 1
    return D[n][m], boxes


def fetch_image(ia, leaf, md, outdir):
    out = {s: f"{outdir}/{leaf:04d}-{s}.webp" for s in SIZES}
    if all(os.path.exists(v) for v in out.values()):
        return out
    url = (f"https://{md['server']}/BookReader/BookReaderImages.php?zip={md['dir']}/{ia}_jp2.zip"
           f"&file={ia}_jp2/{ia}_{leaf:04d}.jp2&id={ia}&scale=1&rotate=0")
    im = Image.open(io.BytesIO(requests.get(url, timeout=300).content)).convert("RGB")
    for s in SIZES:
        c = im.copy()
        c.thumbnail((s, s * 2))
        c.save(out[s], "WEBP", quality=78 if s > 1000 else 74, method=6)
    return out


def run(tid):
    ia, path, filt, scan_note = TABLES[tid]
    md = meta(ia)
    pgs = pages(ia)
    ents = entries(path, filt)
    idxs, scores = locate(pgs, ents)
    boxes = align(pgs, idxs, ents)
    outdir = f"{OUT_IMG}/{tid}"
    os.makedirs(outdir, exist_ok=True)
    with ThreadPoolExecutor(4) as ex:
        list(ex.map(lambda pi: fetch_image(ia, pgs[pi]["leaf"], md, outdir), idxs))
    res = dict(table=tid, ia=ia, scan_note=scan_note,
               ia_title=md.get("metadata", {}).get("title"), contributor=md.get("metadata", {}).get("contributor"),
               rights=md.get("metadata", {}).get("possible-copyright-status") or md.get("metadata", {}).get("rights"),
               pages=[dict(leaf=pgs[pi]["leaf"], w=pgs[pi]["w"], h=pgs[pi]["h"],
                           img={str(s): f"/scans/{tid}/{pgs[pi]['leaf']:04d}-{s}.webp" for s in SIZES},
                           score=scores[pi]) for pi in idxs],
               boxes=boxes, n_entries=len(ents), n_aligned=len(boxes))
    json.dump(res, open(f"{OUT_JSON}/{tid}.json", "w"), indent=1)
    return tid, len(idxs), len(ents), len(boxes), [pgs[pi]["leaf"] for pi in idxs]


if __name__ == "__main__":
    os.makedirs(OUT_JSON, exist_ok=True)
    os.makedirs(RAW, exist_ok=True)
    ids = sys.argv[1:] or list(TABLES)
    for tid in ids:
        try:
            t, np_, ne, nb, leaves = run(tid)
            print(f"{t:10} pages={np_:2d} leaves={leaves[:8]}{'…' if len(leaves) > 8 else ''} aligned {nb}/{ne}")
        except Exception as e:
            print(f"{tid:10} FAILED {type(e).__name__}: {e}")
