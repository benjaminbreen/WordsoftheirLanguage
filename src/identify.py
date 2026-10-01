"""Concept-conditioned lexical retrieval of a historical vocabulary against ASJP.

1. Map printed glosses to ASJP's 100 concepts (keeping the printed gloss).
2. Reduce both historical spellings and ASJP transcriptions to Dolgopolsky-style
   consonant classes (vowels dropped), which is robust to orthographic noise.
3. For every ASJP doculect sharing >= MIN_OVERLAP concepts, compute LDND
   (mean normalised Levenshtein on same-concept pairs / on different-concept pairs).
4. Aggregate the best doculects up the Glottolog classification into hierarchical
   support, with abstention when the leaf level is not decisive.
"""
import csv
import re
import sys
import json
import unicodedata
import collections

import polars as pl
from rapidfuzz.distance import Levenshtein

MIN_OVERLAP = 6

# --- concept mapping ------------------------------------------------------------
CONCEPTS = {
    "I": "*I", "thou": "*you", "you": "*you", "we": "*we", "this": "this", "that": "that",
    "who": "who", "what": "what", "not": "not", "no": "not", "all": "all", "many": "many",
    "one": "*one", "two": "*two", "great": "big", "big": "big", "long": "long", "little": "small",
    "small": "small", "woman": "woman", "wife": "woman", "man": "man", "person": "*person",
    "fish": "*fish", "bird": "bird", "fowl": "bird", "dog": "*dog", "louse": "*louse", "lice": "*louse",
    "tree": "*tree", "seed": "seed", "leaf": "*leaf", "root": "root", "bark": "bark",
    "skin": "*skin", "flesh": "flesh", "meat": "flesh", "blood": "*blood", "bone": "*bone",
    "grease": "grease", "fat": "grease", "egg": "egg", "horn": "*horn", "tail": "tail",
    "feather": "feather", "hair": "hair", "head": "head", "ear": "*ear", "eye": "*eye",
    "nose": "*nose", "mouth": "mouth", "tooth": "*tooth", "teeth": "*tooth", "tongue": "*tongue",
    "claw": "claw", "nail": "claw", "foot": "foot", "feet": "foot", "knee": "*knee", "hand": "*hand",
    "belly": "belly", "neck": "neck", "breast": "*breasts", "breasts": "*breasts", "dug": "*breasts",
    "pap": "*breasts", "heart": "heart", "liver": "*liver", "drink": "*drink", "eat": "eat",
    "bite": "bite", "see": "*see", "hear": "*hear", "know": "know", "sleep": "sleep",
    "die": "*die", "dead": "*die", "kill": "kill", "swim": "swim", "fly": "fly", "walk": "walk",
    "come": "*come", "lie": "lie", "sit": "sit", "stand": "stand", "give": "give", "say": "say",
    "sun": "*sun", "moon": "moon", "star": "*star", "water": "*water", "rain": "rain",
    "stone": "*stone", "sand": "sand", "earth": "earth", "ground": "earth", "land": "earth",
    "cloud": "cloud", "smoke": "smoke", "fire": "*fire", "ashes": "ash", "ash": "ash",
    "burn": "burn", "path": "*path", "way": "*path", "mountain": "*mountain", "hill": "*mountain",
    "red": "red", "green": "green", "yellow": "yellow", "white": "white", "black": "black",
    "night": "*night", "hot": "hot", "cold": "cold", "full": "*full", "new": "*new",
    "good": "good", "round": "round", "dry": "dry", "name": "*name",
}

SPELL = [  # early-modern spelling -> modern, applied word by word
    (r"^vv", "w"), (r"vv", "w"), (r"^v(?=[^aeiou])", "u"), (r"(?<=[^aeiou])v(?=[^aeiou]|$)", "u"),
    (r"ie$", "y"), (r"e$", ""), (r"(.)\1$", r"\1"),
]
NORM = {"sunn": "sun", "sun": "sun", "moon": "moon", "mon": "moon", "fir": "fire", "fyr": "fire",
        "wat": "water", "watr": "water", "her": "hair", "hayr": "hair", "hed": "head", "eie": "eye",
        "ey": "eye", "eyes": "eye", "eies": "eye", "nos": "nose", "mouth": "mouth", "tooth": "tooth",
        "tong": "tongue", "tongu": "tongue", "hand": "hand", "hands": "hand", "fot": "foot",
        "foot": "foot", "feet": "foot", "fet": "foot", "ston": "stone", "stoon": "stone",
        "dog": "dog", "dogg": "dog", "fish": "fish", "fishe": "fish", "tre": "tree", "tree": "tree",
        "lea": "leaf", "leaf": "leaf", "leav": "leaf", "lea": "leaf", "blod": "blood", "bloud": "blood",
        "bon": "bone", "skinn": "skin", "skin": "skin", "erth": "earth", "earth": "earth",
        "grownd": "ground", "ground": "ground", "starr": "star", "star": "star", "starre": "star",
        "rayn": "rain", "rain": "rain", "rayne": "rain", "smok": "smoke", "nyght": "night",
        "night": "night", "nyt": "night", "on": "one", "one": "one", "two": "two", "tow": "two",
        "womann": "woman", "woman": "woman", "wif": "wife", "man": "man", "manne": "man",
        "brest": "breast", "brests": "breast", "kne": "knee", "kne": "knee", "nam": "name",
        "nayl": "nail", "nayles": "nail", "nails": "nail", "bird": "bird", "byrd": "bird",
        "fowl": "fowl", "fowle": "fowl", "egg": "egg", "egge": "egg", "horn": "horn", "hornes": "horn",
        "tayl": "tail", "fether": "feather", "feather": "feather", "hart": "heart", "heart": "heart",
        "lyuer": "liver", "liuer": "liver", "drink": "drink", "drinck": "drink", "eat": "eat",
        "et": "eat", "sleep": "sleep", "slep": "sleep", "kill": "kill", "giu": "give", "giue": "give",
        "come": "come", "com": "come", "sand": "sand", "hill": "hill", "mountain": "mountain",
        "mountayn": "mountain", "whit": "white", "whyt": "white", "blak": "black", "black": "black",
        "red": "red", "redd": "red", "grene": "green", "gren": "green", "yelow": "yellow",
        "hot": "hot", "hott": "hot", "cold": "cold", "good": "good", "god": None, "great": "great",
        "litl": "little", "littl": "little", "long": "long", "new": "new", "newe": "new",
        "bely": "belly", "belly": "belly", "nek": "neck", "neck": "neck", "neck": "neck",
        "lous": "louse", "lyce": "lice", "lic": "lice", "roote": "root", "root": "root", "bark": "bark",
        "flesh": "flesh", "fleshe": "flesh", "meat": "meat", "meate": "meat", "path": "path",
        "way": "way", "wey": "way", "cloud": "cloud", "clowd": "cloud", "ash": "ash", "ashes": "ashes",
        "dead": "dead", "ded": "dead", "dy": "die", "dye": "die", "see": "see", "se": "see",
        "here": "hear", "hear": "hear", "sit": "sit", "sitt": "sit", "stand": "stand",
        "thou": "thou", "yow": "you", "you": "you", "we": "we", "wee": "we", "not": "not", "no": "no",
        "all": "all", "al": "all", "many": "many", "mani": "many", "this": "this", "that": "that",
        "who": "who", "what": "what", "whatt": "what",
        }
STOPS = {"a", "an", "the", "to", "my", "his", "their", "your", "thy", "of", "it", "is", "or", "and"}


def norm_word(w):
    w = unicodedata.normalize("NFKD", w.lower())
    w = "".join(c for c in w if c.isalpha())
    if w in NORM and NORM[w]:
        return NORM[w]
    for a, b in SPELL:
        w = re.sub(a, b, w)
    return NORM.get(w, w)


def gloss_to_concepts(gloss: str):
    """Return set of ASJP concept names for a printed gloss; only short glosses qualify."""
    words = [w for w in re.findall(r"[A-Za-zÀ-ÿ]+", gloss) if w.lower() not in STOPS]
    if not words or len(words) > 3:
        return set()
    out = set()
    for w in words:
        n = norm_word(w)
        if n in CONCEPTS:
            out.add(CONCEPTS[n])
    # "sunne or moone" maps to both; but multiword glosses like "a fish with hornes" shouldn't
    if len(words) > 1 and not re.search(r"\bor\b", gloss.lower()):
        return set() if len(out) != 1 or len(words) > 2 else out
    return out


# --- sound classes ------------------------------------------------------------------
def classes_historical(form: str, collector_profile: str = "english", vowels: bool = False) -> str:
    """Coarse consonant-class string from a European-orthography spelling."""
    s = unicodedata.normalize("NFKD", form.lower())
    s = "".join(c for c in s if c.isalpha())
    if collector_profile == "french":
        rules = [("sch", "S"), ("ch", "S"), ("gn", "N"), ("qu", "K"), ("ou", "u"), ("j", "S"),
                 ("x", "KS"), ("y", "i")]
    else:
        rules = [("tch", "K"), ("sch", "S"), ("sh", "S"), ("ch", "K"), ("th", "T"), ("ph", "P"),
                 ("gh", "K"), ("ck", "K"), ("qu", "KW"), ("x", "KS"), ("wh", "W"), ("j", "K")]
    for a, b in rules:
        s = s.replace(a, b)
    out = []
    for i, ch in enumerate(s):
        nxt = s[i + 1] if i + 1 < len(s) else ""
        prv = s[i - 1] if i else ""
        if ch in "aeiouáéíóúàèìòùâêîôûäëïöü":
            if ch == "u" and prv and prv in "aeiou" and nxt in "aeiou" and nxt:
                out.append("W")
            elif vowels:
                out.append("V")
            continue
        if ch == "v":
            out.append("W" if (nxt and nxt in "aeiou") else "")
            continue
        if ch == "y":
            out.append("J" if (nxt and nxt in "aeiou") else "")
            continue
        if ch == "c":
            out.append("S" if nxt in ("e", "i", "y") and nxt else "K")
            continue
        m = {"p": "P", "b": "P", "f": "P", "t": "T", "d": "T", "s": "S", "z": "S", "k": "K",
             "g": "K", "q": "K", "m": "M", "n": "N", "r": "R", "l": "R", "w": "W", "h": "",
             "S": "S", "K": "K", "T": "T", "P": "P", "N": "N", "W": "W"}
        out.append(m.get(ch, ""))
    res = "".join(out)
    return re.sub(r"(.)\1+", r"\1", res)


ASJP_MAP = {**{c: "P" for c in "pbf"}, "v": "W", "m": "M", "w": "W", "8": "T", "4": "N",
            **{c: "T" for c in "td"}, **{c: "S" for c in "szSZ"}, **{c: "K" for c in "cCjTkgxqGX"},
            "5": "N", "n": "N", "N": "N", **{c: "R" for c in "rlL"}, "y": "J", "h": "", "7": "", "!": "K"}


def classes_asjp(form: str, vowels: bool = False) -> str:
    s = re.sub(r'[~"*$%]', "", form)
    res = "".join(ASJP_MAP.get(c, "V" if (vowels and c in "ieE3auo") else "") for c in s)
    return re.sub(r"(.)\1+", r"\1", res)


def ldn(a, b):
    if not a and not b:
        return 0.0
    return Levenshtein.distance(a, b) / max(len(a), len(b), 1)


# --- reference data -------------------------------------------------------------
class ASJP:
    def __init__(self):
        f = pl.read_csv("data/raw/asjp_repo/cldf/forms.csv", infer_schema_length=0,
                        columns=["Language_ID", "Parameter_ID", "Form", "Loan"])
        p = pl.read_csv("data/raw/asjp_repo/cldf/parameters.csv", infer_schema_length=0)
        f = f.join(p.select(pl.col("ID").alias("Parameter_ID"), pl.col("Name").alias("concept")),
                   on="Parameter_ID")
        self.lang = pl.read_csv("data/raw/asjp_repo/cldf/languages.csv", infer_schema_length=0)
        self.words = collections.defaultdict(lambda: collections.defaultdict(list))
        for lid, c, form, loan in f.select("Language_ID", "concept", "Form", "Loan").iter_rows():
            if loan == "true":
                continue
            self.words[lid][c].append(classes_asjp(form))
        self.info = {r["ID"]: r for r in self.lang.iter_rows(named=True)}


def score_list(entries, ref: ASJP, exclude=(), profile="english"):
    """entries: list of (concept, class_string). Returns ranked doculects."""
    by_c = collections.defaultdict(list)
    for c, cls in entries:
        if cls:
            by_c[c].append(cls)
    concepts = list(by_c)
    res = []
    for lid, wd in ref.words.items():
        if lid in exclude:
            continue
        shared = [c for c in concepts if c in wd]
        if len(shared) < MIN_OVERLAP:
            continue
        same = [min(ldn(h, r) for h in by_c[c] for r in wd[c]) for c in shared]
        diff = [min(ldn(h, r) for h in by_c[c1] for r in wd[c2])
                for c1 in shared for c2 in shared if c1 != c2]
        dsame = sum(same) / len(same)
        ddiff = sum(diff) / len(diff) if diff else 1.0
        res.append((dsame / max(ddiff, 1e-6), dsame, len(shared), lid))
    res.sort()
    return res


def hierarchical(ranked, ref: ASJP, top=20):
    """Share of the top-N doculects (rank-weighted) agreeing at each classification depth."""
    paths = []
    for i, (ldnd, _, n, lid) in enumerate(ranked[:top]):
        info = ref.info[lid]
        fam = info["Family"] or ""
        cls = (info["classification_glottolog"] or "").split(",")
        path = [fam] + [c for c in cls if c and c != fam] + [info["Glottolog_Name"] or lid]
        paths.append((1.0 / (i + 1), path))
    W = sum(w for w, _ in paths)
    out = []
    depth = 0
    prefix = []
    while True:
        cnt = collections.Counter()
        for w, p in paths:
            if p[:depth] == prefix and len(p) > depth:
                cnt[p[depth]] += w
        if not cnt:
            break
        node, wt = cnt.most_common(1)[0]
        out.append((node, round(wt / W, 2)))
        prefix = prefix + [node]
        depth += 1
        if wt / W < 0.5:
            break
    return out


def load_entries(path):
    rows = list(csv.DictReader(open(path, encoding="utf-8")))
    ents = []
    for r in rows:
        for c in gloss_to_concepts(r["gloss_as_printed"]):
            ents.append((c, r["form_as_printed"]))
    return ents


if __name__ == "__main__":
    path = sys.argv[1]
    exclude = set(sys.argv[2].split(",")) if len(sys.argv) > 2 and sys.argv[2] else set()
    profile = sys.argv[3] if len(sys.argv) > 3 else "english"
    ref = ASJP()
    raw = load_entries(path)
    ents = [(c, classes_historical(f, profile)) for c, f in raw]
    print(f"{len(raw)} concept-mapped forms, {len({c for c, _ in raw})} distinct concepts")
    for c, f in raw[:60]:
        print(f"   {c:10} {f:20} {classes_historical(f, profile)}")
    ranked = score_list(ents, ref, exclude, profile)
    for ldnd, ds, n, lid in ranked[:15]:
        i = ref.info[lid]
        print(f"{ldnd:.3f} {ds:.3f} n={n:2d} {lid:40} {i['Family']} | {(i['classification_glottolog'] or '')[:70]}")
    print("HIERARCHY:", hierarchical(ranked, ref))
