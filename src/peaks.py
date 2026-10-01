"""Locate the densest stretch of vocabulary evidence inside a candidate span.

Re-tags tokens in the span exactly as detect.py does and returns the start of the
WIDTH-character window holding the most rare-form/gloss events (or naming cues).
"""
import bisect

from glosses import GLOSSES, TOKEN_RE
from detect import CUES, K


def event_offsets(text, rare):
    toks = [(m.group(), m.start()) for m in TOKEN_RE.finditer(text)]
    tags = []
    for t, _ in toks:
        lt = t.lower()
        tags.append("G" if lt in GLOSSES else "R" if lt in rare else "O")
    offs = set()
    n = len(toks)
    for i, tg in enumerate(tags):
        if tg != "R":
            continue
        lo, hi = max(0, i - K), min(n, i + K + 1)
        if "G" in tags[lo:hi] or any(toks[j][0].lower() in CUES for j in range(max(0, i - 5), i)):
            offs.add(toks[i][1])
    return sorted(offs)


def peak_windows(text, rare, start, end, width=2500, max_windows=3):
    """Up to max_windows non-overlapping windows (char offsets) ranked by event count."""
    seg = text[start:end]
    offs = event_offsets(seg, rare)
    if not offs:
        return [(start, 0)]
    cands = []
    for o in offs:
        c = bisect.bisect_left(offs, o + width) - bisect.bisect_left(offs, o)
        cands.append((c, o))
    cands.sort(reverse=True)
    chosen = []
    for c, o in cands:
        if all(abs(o - p) >= width for p, _ in chosen):
            chosen.append((o, c))
        if len(chosen) == max_windows:
            break
    return [(start + max(0, o - 300), c) for o, c in chosen]
