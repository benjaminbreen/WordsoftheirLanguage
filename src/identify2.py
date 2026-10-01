"""Blind identification of a historical wordlist against ASJP + Lexibank.

Pipeline
  1. printed gloss -> Concepticon gloss (printed gloss is kept alongside)
  2. printed form -> consonant-class string (orthography profile: english | french | dutch ...)
  3. list-internal affix stripping: class-suffixes/prefixes shared by >= 25% of forms
     (e.g. Laurentian body-part '-ascon') are removed, since the collector recorded them
     on every noun and they swamp the comparison
  4. LDND against every reference doculect sharing >= MIN_OVERLAP concepts
  5. permutation test (concept labels shuffled within the historical list) for the top
     candidates: is the similarity concept-specific, or just shared phonotactics?
  6. hierarchical support over Glottolog paths of significant candidates; abstain if none

Usage: python src/identify2.py entries.csv [--profile english] [--exclude ID,ID] [--json out.json]
"""
import argparse
import collections
import csv
import json
import re
import unicodedata

import numpy as np
import polars as pl
from rapidfuzz.process import cdist
from rapidfuzz.distance import Levenshtein

import glottolog
from identify import classes_historical, classes_asjp, SPELL, NORM

MIN_OVERLAP = 8
Z_THRESHOLD = 4.6   # 95th pct of best-z over shuffled-list nulls (out/benchmark.json, vowels=True)
TOP_TEST = 40
N_PERM = 300
ALPHA = 0.01

# ----------------------------------------------------------------------- concepts
NUMERALS = {"1": "ONE", "2": "TWO", "3": "THREE", "4": "FOUR", "5": "FIVE", "6": "SIX",
            "7": "SEVEN", "8": "EIGHT", "9": "NINE", "10": "TEN", "20": "TWENTY", "100": "HUNDRED"}
# spelled-out and early-modern numerals
NUMWORDS = {"one": "ONE", "two": "TWO", "three": "THREE", "thre": "THREE", "four": "FOUR",
            "foure": "FOUR", "five": "FIVE", "fiue": "FIVE", "six": "SIX", "sixe": "SIX",
            "seven": "SEVEN", "seuen": "SEVEN", "eight": "EIGHT", "nine": "NINE", "ten": "TEN",
            "twenty": "TWENTY", "hundred": "HUNDRED"}
# common early-modern/encounter glosses whose Concepticon gloss isn't the plain word
EXTRA = {"sunne": "SUN", "moone": "MOON", "heauen": "SKY", "heaven": "SKY", "skie": "SKY",
         "canoa": "CANOE", "canow": "CANOE", "canoe": "CANOE", "boate": "BOAT", "ship": "BOAT",
         "shippe": "BOAT", "tabacco": "TOBACCO", "tobaco": "TOBACCO", "tobacco": "TOBACCO",
         "deere": "DEER", "beuer": "BEAVER", "beauer": "BEAVER", "corne": "MAIZE", "maiz": "MAIZE",
         "maize": "MAIZE", "wheat": "MAIZE", "knyfe": "KNIFE", "knife": "KNIFE", "bowe": "BOW",
         "arrowe": "ARROW", "hatchet": "AXE", "axe": "AXE", "hatchets": "AXE", "kettle": "POT",
         "heares": "HAIR", "haire": "HAIR", "heare": "HAIR", "fyre": "FIRE", "eies": "EYE",
         "eyes": "EYE", "eares": "EAR", "teeth": "TOOTH", "feete": "FOOT", "feet": "FOOT",
         "handes": "HAND", "fingers": "FINGER", "nailes": "FINGERNAIL", "nayles": "FINGERNAIL",
         "legges": "LEG", "knees": "KNEE", "armes": "ARM", "lippes": "LIP", "brests": "BREAST",
         "bellie": "BELLY", "throate": "THROAT", "browe": "EYEBROW", "beard": "BEARD",
         "bearde": "BEARD", "wife": "WIFE", "husband": "HUSBAND", "childe": "CHILD",
         "sonne": "SON", "dogge": "DOG", "foxe": "FOX", "wolfe": "WOLF", "fishe": "FISH",
         "fowle": "BIRD", "fowles": "BIRD", "egge": "EGG", "riuer": "RIVER", "sea": "SEA",
         "salt": "SALT", "bread": "BREAD", "meate": "MEAT", "flesh": "MEAT", "day": "DAY",
         "night": "NIGHT", "yesterday": "YESTERDAY", "to-morrow": "TOMORROW",
         "tomorrow": "TOMORROW", "yea": "YES", "yes": "YES", "no": "NO", "god": "GOD",
         "deuill": "DEVIL", "devil": "DEVIL", "copper": "COPPER", "iron": "IRON", "yron": "IRON",
         "pipe": "TOBACCO PIPE", "house": "HOUSE", "houses": "HOUSE", "towne": "VILLAGE",
         "woods": "FOREST", "wooddes": "FOREST", "leaues": "LEAF", "starres": "STAR",
         "starre": "STAR", "stars": "STAR", "raine": "RAIN", "snowe": "SNOW", "winde": "WIND",
         "stones": "STONE", "bones": "BONE", "eate": "EAT", "drinke": "DRINK", "sleepe": "SLEEP",
         "goe": "GO", "giue": "GIVE", "speake": "SPEAK", "weepe": "CRY", "greene": "GREEN",
         "lobster": "LOBSTER", "seale": "SEAL", "whale": "WHALE", "otter": "OTTER",
         "stomacke": "STOMACH", "thighes": "THIGH", "tongue": "TONGUE", "face": "FACE"}
STOPW = {"a", "an", "the", "to", "my", "his", "their", "your", "thy", "of", "it", "is", "or",
         "and", "great", "little", "small", "very"}


class ConceptMapper:
    def __init__(self):
        c = pl.read_csv("data/raw/lexibank_repo/cldf/concepts.csv", infer_schema_length=0)
        self.glosses = set(c["Concepticon_Gloss"].to_list())
        self.single = {}
        for g in self.glosses:
            base = re.sub(r"\s*\(.*?\)", "", g).strip().lower()
            if base and " " not in base:
                # prefer the plainest concept for each word (shortest gloss)
                if base not in self.single or len(g) < len(self.single[base]):
                    self.single[base] = g

    def word(self, w):
        w0 = unicodedata.normalize("NFKD", w.lower())
        w0 = "".join(ch for ch in w0 if ch.isalpha() or ch == "-")
        if w0 in NUMWORDS:
            return NUMWORDS[w0]
        if w0 in EXTRA:
            return EXTRA[w0]
        cands = [w0]
        n = NORM.get(w0)
        if n:
            cands.append(n)
        x = w0
        for a, b in SPELL:
            x = re.sub(a, b, x)
        cands += [x, w0.rstrip("e"), re.sub(r"(es|s)$", "", w0), re.sub(r"(.)\1e?$", r"\1", w0),
                  w0.replace("v", "u"), w0.replace("u", "v"), w0.replace("y", "i"), w0.replace("ie", "y")]
        for cnd in cands:
            if cnd in EXTRA:
                return EXTRA[cnd]
            if cnd in self.single:
                return self.single[cnd]
        return None

    def __call__(self, gloss):
        g = gloss.strip()
        if g.strip(". ") in NUMERALS:
            return {NUMERALS[g.strip(". ")]}
        words = [w for w in re.findall(r"[A-Za-zÀ-ÿ\-]+", g) if w.lower() not in STOPW]
        if not words or len(words) > 3:
            return set()
        if re.search(r"\bor\b", g.lower()):
            return {c for c in (self.word(w) for w in words) if c}
        if len(words) == 1:
            c = self.word(words[0])
            return {c} if c else set()
        return set()  # multiword glosses ("a fish with hornes") are not basic concepts


# ----------------------------------------------------------------------- reference
VOWELS = True


def dolgo_to_classes(s):
    s = re.sub(r"[+H1_0]", "", s or "")
    if not VOWELS:
        s = s.replace("V", "")
    return re.sub(r"(.)\1+", r"\1", s)


def hist_classes(form, profile):
    return classes_historical(form, profile, vowels=VOWELS)


def asjp_classes(form):
    return classes_asjp(form, vowels=VOWELS)


class Reference:
    """doculect id -> {concept gloss -> [class strings]} with Glottolog paths."""

    def __init__(self, use=("asjp", "lexibank")):
        self.words = collections.defaultdict(lambda: collections.defaultdict(list))
        self.glotto, self.name, self.src = {}, {}, {}
        if "asjp" in use:
            f = pl.read_csv("data/raw/asjp_repo/cldf/forms.csv", infer_schema_length=0,
                            columns=["Language_ID", "Parameter_ID", "Form", "Loan"])
            p = pl.read_csv("data/raw/asjp_repo/cldf/parameters.csv", infer_schema_length=0)
            pm = dict(zip(p["ID"], p["Concepticon_Gloss"]))
            for lid, pid, form, loan in f.iter_rows():
                if loan == "true" or pid not in pm:
                    continue
                self.words["asjp:" + lid][pm[pid]].append(asjp_classes(form))
            for r in pl.read_csv("data/raw/asjp_repo/cldf/languages.csv", infer_schema_length=0).iter_rows(named=True):
                k = "asjp:" + r["ID"]
                self.glotto[k], self.name[k], self.src[k] = r["Glottocode"], r["ID"], "ASJP"
        if "lexibank" in use:
            f = pl.read_parquet("data/work/lexibank_forms.parquet")
            c = pl.read_csv("data/raw/lexibank_repo/cldf/concepts.csv", infer_schema_length=0)
            cm = dict(zip(c["ID"], c["Concepticon_Gloss"]))
            for lid, pid, dc, loan in f.iter_rows():
                if loan == "true" or pid not in cm or not dc:
                    continue
                self.words["lb:" + lid][cm[pid]].append(dolgo_to_classes(dc))
            for r in pl.read_csv("data/raw/lexibank_repo/cldf/languages.csv", infer_schema_length=0).iter_rows(named=True):
                k = "lb:" + r["ID"]
                self.glotto[k], self.name[k], self.src[k] = r["Glottocode"], r["Name"], "Lexibank"

    def path(self, k):
        g = self.glotto.get(k)
        return glottolog.path_names(g) if g else [self.name.get(k, k)]


# ----------------------------------------------------------------------- affixes
def strip_affixes(forms, min_share=0.25, min_n=4):
    """forms: list of class strings. Remove class-suffixes/prefixes recurring across the list."""
    out = list(forms)
    removed = []
    for side in ("suffix", "prefix"):
        best = None
        for L in (4, 3, 2):
            cnt = collections.Counter(
                (f[-L:] if side == "suffix" else f[:L]) for f in out if len(f) >= L + 1)
            if not cnt:
                continue
            aff, n = cnt.most_common(1)[0]
            if n >= min_n and n / len(out) >= min_share:
                best = aff
                break
        if best:
            removed.append((side, best))
            out = [(f[:-len(best)] if side == "suffix" else f[len(best):])
                   if (f.endswith(best) if side == "suffix" else f.startswith(best)) and len(f) > len(best)
                   else f for f in out]
    return out, removed


# ----------------------------------------------------------------------- scoring
def ldnd_matrix(hist, refw):
    """hist: list of (concept, cls). refw: {concept: [cls]}. Returns (ldnd, dsame, n_shared)."""
    concepts = sorted({c for c, _ in hist if c in refw})
    if len(concepts) < MIN_OVERLAP:
        return None
    hforms = [[h for c2, h in hist if c2 == c] for c in concepts]
    rforms = [refw[c] for c in concepts]
    hflat = [h for hs in hforms for h in hs]
    rflat = [r for rs in rforms for r in rs]
    hidx = np.repeat(np.arange(len(concepts)), [len(h) for h in hforms])
    ridx = np.repeat(np.arange(len(concepts)), [len(r) for r in rforms])
    D = cdist(hflat, rflat, scorer=Levenshtein.normalized_distance, workers=1)
    k = len(concepts)
    M = np.full((k, k), 1.0)
    # min over forms for each (hist concept, ref concept)
    for i in range(k):
        Di = D[hidx == i]
        if Di.size == 0:
            continue
        mn = Di.min(axis=0)
        np.minimum.at(M[i], ridx, mn)
    return M


def ldnd_from(M, perm=None):
    k = M.shape[0]
    if perm is not None:
        M = M[perm]
    same = np.trace(M) / k
    diff = (M.sum() - np.trace(M)) / (k * k - k)
    return same / max(diff, 1e-6), same


def identify(entries, ref, exclude=(), profile="english", seed=0):
    """entries: list of (printed_gloss, printed_form). Returns dict result."""
    cm = ConceptMapper()
    mapped = []
    for g, f in entries:
        for c in cm(g):
            mapped.append((c, f))
    cls = [hist_classes(f, profile) for _, f in mapped]
    cls2, removed = strip_affixes(cls)
    hist = [(c, x) for (c, _), x in zip(mapped, cls2) if x]
    scores = []
    for k, refw in ref.words.items():
        if k in exclude or (ref.glotto.get(k) or "") in exclude:
            continue
        M = ldnd_matrix(hist, refw)
        if M is None:
            continue
        l, s = ldnd_from(M)
        scores.append((l, s, M.shape[0], k, M))
    scores.sort(key=lambda x: x[0])
    rng = np.random.default_rng(seed)
    tested = []
    for l, s, n, k, M in scores[:TOP_TEST]:
        null = np.array([ldnd_from(M, rng.permutation(n))[0] for _ in range(N_PERM)])
        p = (1 + (null <= l).sum()) / (N_PERM + 1)
        z = (null.mean() - l) / (null.std() + 1e-9)
        tested.append(dict(doculect=k, name=ref.name.get(k), source=ref.src.get(k),
                           glottocode=ref.glotto.get(k), path=ref.path(k), ldnd=round(float(l), 3),
                           dsame=round(float(s), 3), n=int(n), p=round(float(p), 4), z=round(float(z), 2)))
    tested.sort(key=lambda t: -t["z"])
    sig = [t for t in tested if t["p"] <= ALPHA and t["z"] >= Z_THRESHOLD]
    lead = tested[0] if tested else None
    return dict(n_entries=len(entries), n_mapped=len(mapped), n_concepts=len({c for c, _ in hist}),
                affixes_removed=removed, candidates=tested, hierarchy=hierarchy(sig),
                status="resolved" if sig else "abstain",
                leading=lead and dict(name=lead["name"], family=lead["path"][0], z=lead["z"]))


def hierarchy(sig, min_share=0.6):
    """Walk Glottolog paths of significant candidates weighted by z; stop when support < min_share."""
    if not sig:
        return []
    wt = lambda t: t["z"] - Z_THRESHOLD + 0.5
    W = sum(wt(t) for t in sig)
    out, prefix = [], []
    while True:
        cnt = collections.Counter()
        for t in sig:
            p = t["path"]
            if p[:len(prefix)] == prefix and len(p) > len(prefix):
                cnt[p[len(prefix)]] += wt(t)
        if not cnt:
            break
        node, w = cnt.most_common(1)[0]
        share = w / W
        out.append((node, round(share, 2)))
        if share < min_share:
            break
        prefix.append(node)
    return out


def read_entries(path):
    rows = list(csv.DictReader(open(path, encoding="utf-8")))
    return [(r["gloss_as_printed"], r["form_as_printed"]) for r in rows
            if r.get("gloss_as_printed") and r.get("form_as_printed")]


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("entries")
    ap.add_argument("--profile", default="english")
    ap.add_argument("--exclude", default="")
    ap.add_argument("--json")
    a = ap.parse_args()
    ref = Reference()
    res = identify(read_entries(a.entries), ref, set(x for x in a.exclude.split(",") if x), a.profile)
    print(f"{res['n_entries']} entries, {res['n_mapped']} mapped, {res['n_concepts']} concepts; "
          f"affixes removed: {res['affixes_removed']}")
    for t in res["candidates"][:15]:
        flag = "*" if t["p"] <= ALPHA else " "
        print(f"{flag} ldnd={t['ldnd']:.3f} n={t['n']:3d} p={t['p']:.3f} z={t['z']:5.2f} "
              f"{t['source']:8} {t['name'][:28]:28} {' > '.join(t['path'][:4])[:70]}")
    print("STATUS:", res["status"], "| HIERARCHY:", " > ".join(f"{n} ({s})" for n, s in res["hierarchy"]))
    if a.json:
        json.dump(res, open(a.json, "w"), ensure_ascii=False, indent=1)
