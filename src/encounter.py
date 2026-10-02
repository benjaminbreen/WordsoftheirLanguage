"""Entry-level detectors for elicitation and contact artifacts in historical wordlists.

For every extracted entry (gloss, form) the detectors ask:

  D1 interactional  - is the gloss itself a speech act (question, greeting, "I know not")?   [phrase]
                    - does a form glossed as a thing match the target language's word for
                      WHAT / WHO / THIS / THAT / NOT / NO / GIVE / I / THOU ...?               [interactional_as_lexeme]
                    - does one form recur under >= 3 unrelated glosses?                    [recurrent_form]
  D2 ostension      - does the form match a *neighbouring* concept (nose/face, finger/nail,
                      sun/day ...) much better than its own gloss?                         [neighbour_concept]
  D3 body           - a recurring affix concentrated on body-part entries (e.g. da- 'my').  [list level]
  D4 contact        - does the form match a European or lingua-franca donor word for the
                      same concept much better than the target language's word?            [loan:<donor>]
  D5 intermediary   - per printed section, share of entries closer to a lingua franca
                      than to the target.                                                  [section level]
  D6 circulation    - forms that recur in lists of *different* language families.           [circulating]

Reference data: ASJP + Lexibank via identify2.Reference. Distances are normalised Levenshtein
over sound-class strings (consonant classes + vowel slots).
Outputs: data/work/encounter/flags.parquet, data/work/encounter/lists.json
"""
import collections
import csv
import json
import os
import re
import unicodedata

import polars as pl
from rapidfuzz.distance import Levenshtein

import glottolog
import identify2 as I
from build_site_data import LISTS, read_rows

OUT = "data/work/encounter"

# Target doculects for lists where blind identification abstained (assigned from the literature;
# detection, unlike identification, does not need to be blind).
ASSIGNED_TARGET = {
    "cartier": ["asjp:WYANDOT", "asjp:WENDAT_HURON", "asjp:MOHAWK", "asjp:ONONDAGA"],
    "smith_map": ["asjp:POWHATAN_UnnamedInSource"],
    "williams": ["asjp:WAMPANOAG_NATICK", "asjp:MOHEGAN"],
    "knox": ["asjp:SINHALA"],
    "gthomas": ["asjp:UNAMI_UnnamedInSource", "asjp:DELAWARE_MUNSEE", "asjp:PIDGIN_DELAWARE"],
    "ludolf_gallan": [],  # filled by name lookup below
}

DONORS = {  # name -> doculect keys (richest first)
    "Portuguese": ["lb:keypano-Portuguese", "lb:northeuralex-por"],
    "Spanish": ["lb:keypano-Spanish", "lb:northeuralex-spa"],
    "Basque": ["lb:idssegmented-basque", "lb:northeuralex-eus"],
    "Dutch": ["lb:wold-Dutch", "lb:northeuralex-nld"],
    "French": ["lb:northeuralex-fra"],
    "English": ["lb:wold-English", "lb:northeuralex-eng"],
    "Italian": ["lb:northeuralex-ita"],
    "German": ["lb:northeuralex-deu"],
    "Latin": ["lb:northeuralex-lat"],
    "Arabic": ["lb:northeuralex-arb"],
    "Persian": ["lb:idssegmented-persian", "lb:northeuralex-pes"],
    "Turkish": ["lb:northeuralex-tur"],
    "Hindi": ["lb:northeuralex-hin"],
    "Tamil": ["lb:northeuralex-tam"],
    "Malay": ["lb:transnewguineaorg-indonesian", "asjp:MELAYU", "asjp:LOW_MALAY_1773"],
    "Nahuatl": ["lb:utoaztecan-ClassicalAztec"],
    "Quechua": ["lb:crossandean-Cuzco"],
    "Tupi": ["lb:tuled-Tupinamba"],
    "Kalina": ["lb:wold-Kalina"],
    "Danish": ["lb:northeuralex-dan"],
    "Swedish": ["lb:northeuralex-swe"],
    "Norwegian": ["lb:northeuralex-nor"],
    "Russian": ["lb:northeuralex-rus"],
    "Finnish": ["lb:idssegmented-finnish", "lb:northeuralex-fin"],
    "Amharic": ["lb:felekesemitic-Amharic"],
    "Geez": ["lb:felekesemitic-Geez"],
    "Swahili": ["lb:wold-Swahili"],
}

# Historically plausible donors per list (contact languages present in that region and period).
NA_EAST = ["French", "Basque", "English", "Dutch", "Spanish", "Portuguese"]
ASIA = ["Portuguese", "Dutch", "Spanish", "English", "Arabic", "Persian", "Malay", "Hindi", "Tamil"]
REGION_DONORS = {
    "rosier": NA_EAST, "wood": NA_EAST, "williams": NA_EAST, "smith_map": NA_EAST, "gthomas": NA_EAST + ["Swedish"],
    "cartier": ["French", "Basque", "Portuguese", "Spanish"],
    "rochefort": ["Spanish", "Portuguese", "French", "English", "Dutch", "Kalina"],
    "trinidad": ["Spanish", "Portuguese", "French", "English", "Dutch", "Kalina"],
    "tupi_ogilby": ["Portuguese", "Dutch", "Spanish", "French"],
    "chilesian": ["Spanish", "Quechua", "Dutch"],
    "boothby": ["Portuguese", "Arabic", "English", "Dutch", "Swahili"],
    "vanneck": ASIA, "pegu": ASIA, "knox": ASIA,
    "greenland": ["Danish", "Dutch", "German", "English", "Norwegian"],
    "scheffer": ["Swedish", "Norwegian", "Finnish", "Russian", "German", "Danish"],
    "sami_burrough": ["Swedish", "Norwegian", "Finnish", "Russian", "Danish", "English", "Dutch"],
    "ludolf_gallan": ["Arabic", "Amharic", "Geez", "Portuguese", "Italian"],
}
COLEX = json.load(open("data/work/encounter/colex_rates.json")) if os.path.exists("data/work/encounter/colex_rates.json") else {}


def colex_rate(a, b):
    return COLEX.get(f"{a}|{b}", COLEX.get(f"{b}|{a}", 0.0))
LINGUA_FRANCAS = {"Portuguese", "Spanish", "Malay", "Arabic", "Tupi", "Persian", "Turkish"}

INTERACTIONAL = {"WHAT", "WHO", "THIS", "THAT", "NOT", "NO", "YES", "GIVE", "I", "THOU", "YOU",
                 "HERE", "THERE", "WHERE", "HOW", "COME", "TAKE"}
PHRASE_RE = re.compile(
    r"(?i)\b(what|how|who|whither|whence|where|why|which)\b|\?|\bi (?:know|understand|vnderstand|cannot|can not|am|haue|have|will|thank)\b|"
    r"\b(thank|farewell|god be with|good morrow|good morow|come hither|go(?:e)? (?:thy|your|away|we)|sit downe?|give me|giue me|let it alone|how doe|is there)\b")

FIELDS = {
    "head": ["HEAD", "HAIR", "FOREHEAD", "FACE", "EYE", "EYEBROW", "EYELASH", "NOSE", "MOUTH", "LIP",
             "TOOTH", "TONGUE", "EAR", "CHEEK", "CHIN", "BEARD", "NECK", "THROAT", "GUMS"],
    "limb": ["ARM", "HAND", "FINGER", "FINGERNAIL", "THUMB", "PALM OF HAND", "WRIST", "ELBOW", "SHOULDER",
             "LEG", "FOOT", "KNEE", "TOE", "THIGH", "HEEL", "CALF OF LEG"],
    "trunk": ["BELLY", "STOMACH", "BREAST", "BACK", "NAVEL", "CHEST", "HEART", "LIVER", "SKIN", "BONE",
              "BLOOD", "MEAT", "FLESH", "INTESTINES", "PENIS", "VULVA"],
    "sky": ["SUN", "MOON", "STAR", "SKY", "CLOUD", "DAY", "LIGHT", "RAIN", "WIND", "THUNDER", "NIGHT"],
    "ground": ["STONE", "SAND", "EARTH (SOIL)", "MOUNTAIN", "LAND", "GROUND", "DUST", "MUD", "HILL"],
    "water": ["WATER", "SEA", "RIVER", "LAKE", "WAVE", "SALT"],
    "fire": ["FIRE", "SMOKE", "ASH", "FIREWOOD", "BURN", "COAL"],
    "kin": ["FATHER", "MOTHER", "BROTHER", "SISTER", "SON", "DAUGHTER", "CHILD", "MAN", "WOMAN", "WIFE",
            "HUSBAND", "BOY", "GIRL", "PERSON", "OLDER BROTHER", "YOUNGER BROTHER"],
    "plant": ["TREE", "WOOD", "LEAF", "BARK", "ROOT", "FOREST", "BRANCH", "FLOWER", "FRUIT", "SEED"],
}
FIELD_OF = {c: f for f, cs in FIELDS.items() for c in cs}
BODY = set(FIELDS["head"] + FIELDS["limb"] + FIELDS["trunk"])

T_NEIGH, T_GAP = 0.30, 0.30     # ostension: neighbour distance <= T_NEIGH and own - neighbour >= T_GAP
T_LOAN, T_LOAN_GAP = 0.25, 0.25  # contact: donor distance <= T_LOAN and target - donor >= T_LOAN_GAP
MIN_CLS = 4                      # ignore very short class strings for loan / interactional matches


def d(a, b):
    return Levenshtein.normalized_distance(a, b)


def mind(cls, forms):
    return min((d(cls, f) for f in forms), default=None)


def pooled(ref, keys):
    """Pool concept->forms (class strings) and raw forms over several doculects."""
    cls, raw = collections.defaultdict(list), collections.defaultdict(list)
    for k in keys:
        if k not in ref.words:
            continue
        for c, fs in ref.words[k].items():
            cls[c] += fs
            raw[c] += ref.raw[k].get(c, [])
    return cls, raw


def norm_orth(f):
    f = unicodedata.normalize("NFKD", f.lower())
    f = "".join(ch for ch in f if ch.isalpha())
    return f.replace("v", "u").replace("j", "i").replace("y", "i").replace("ck", "k").replace("c", "k")


def main():
    os.makedirs(OUT, exist_ok=True)
    ref = I.Reference()
    cm = I.ConceptMapper()
    names = {k: (ref.name.get(k) or "") for k in ref.words}
    oromo = [k for k, n in names.items() if re.search(r"(?i)oromo", n)]
    ASSIGNED_TARGET["ludolf_gallan"] = sorted(oromo, key=lambda k: -len(ref.words[k]))[:3]
    donor_ref = {n: pooled(ref, [k for k in ks if k in ref.words]) for n, ks in DONORS.items()}
    donor_fam = {}
    for n, ks in DONORS.items():
        g = next((ref.glotto.get(k) for k in ks if ref.glotto.get(k)), None)
        donor_fam[n] = glottolog.family(g) if g else n

    flags, lists_out, all_forms = [], [], []
    for vid, path, prof, excl, filt, prov in LISTS:
        rows = read_rows(path, filt)
        ents = [(r["gloss_as_printed"], r["form_as_printed"]) for r in rows if r.get("gloss_as_printed") and r.get("form_as_printed")]
        res = I.identify(ents, ref, set(excl), prof)
        sig = [t["doculect"] for t in res["candidates"] if t["z"] >= I.Z_THRESHOLD][:3]
        tsource = "identified"
        if not sig:
            sig, tsource = ASSIGNED_TARGET.get(vid, []), "assigned"
        tcls, traw = pooled(ref, sig)
        tfam = glottolog.family(ref.glotto[sig[0]]) if sig and ref.glotto.get(sig[0]) else None
        affixes = res["affixes_removed"]
        # recurrent forms within list
        by_form = collections.defaultdict(set)
        for r in rows:
            for sf in I.split_forms(r["form_as_printed"] or ""):
                by_form[norm_orth(sf)].add((r["gloss_as_printed"] or "").lower().strip(" .,"))
        sec_votes = collections.defaultdict(collections.Counter)
        body_aff = collections.Counter()
        for r in rows:
            g, f = r.get("gloss_as_printed") or "", r.get("form_as_printed") or ""
            if not g or not f:
                continue
            concepts = cm(g)
            base = dict(list=vid, tcp_id=path.rsplit("_", 1)[-1], section=(r.get("section_heading") or "")[:80],
                        gloss=g, form=f, concepts=";".join(sorted(concepts)), extractor_note=r.get("note") or "",
                        target_source=tsource)
            if PHRASE_RE.search(g):
                flags.append(dict(base, kind="phrase", detail="gloss is a speech act or question", score=1.0))
            for sf in I.split_forms(f):
                no = norm_orth(sf)
                all_forms.append((vid, tfam, no, sf, g))
                if len(no) >= 4 and len(by_form[no]) >= 3:
                    flags.append(dict(base, kind="recurrent_form", detail=" | ".join(sorted(by_form[no]))[:200], score=float(len(by_form[no]))))
                cls = I.hist_classes(I.strip_form(sf, affixes), prof)
                if not cls:
                    continue
                # D3: affix on body parts
                if affixes:
                    has = any((sf.lower().startswith(a) if s == "prefix" else sf.lower().endswith(a)) for s, a, _ in affixes)
                    body_aff[(bool(concepts & BODY), has)] += 1
                for c in concepts:
                    own = mind(cls, tcls.get(c, []))
                    # D1b interactional words given for things
                    if c not in INTERACTIONAL and own is not None and len(cls) >= 4 and len(cls.replace("V", "")) >= 2:
                        best = None
                        for ic in INTERACTIONAL:
                            di = mind(cls, tcls.get(ic, []))
                            if di is not None and di <= 0.1 and own - di >= 0.4:
                                if best is None or di < best[0]:
                                    best = (di, ic)
                        if best:
                            ex = traw.get(best[1], [""])[0]
                            flags.append(dict(base, kind="interactional_as_lexeme",
                                              detail=f"matches target {best[1]} ({ex}); own-concept dist {own}", score=round(1 - best[0], 2)))
                    # D2 neighbour concept
                    fld = FIELD_OF.get(c)
                    if fld and own is not None:
                        for c2 in FIELDS[fld]:
                            if c2 == c or c2 not in tcls:
                                continue
                            dn = mind(cls, tcls[c2])
                            if dn is not None and dn <= T_NEIGH and own - dn >= T_GAP:
                                ex = traw.get(c2, [""])[0]
                                rate = colex_rate(c, c2)
                                flags.append(dict(base, kind="neighbour_concept" if rate < 0.01 else "colexification",
                                                  detail=f"{c} printed, matches {c2} ({ex}) at {dn:.2f} vs own {own:.2f}; colex rate {rate:.3f}",
                                                  score=round(own - dn, 2)))
                    # D4 loans
                    if len(cls.replace("V", "")) >= 2 and len(cls) >= MIN_CLS:
                        for dn_name in REGION_DONORS.get(vid, []):
                            dcls, draw = donor_ref[dn_name]
                            if tfam and donor_fam.get(dn_name) == tfam:
                                continue
                            dd = mind(cls, dcls.get(c, []))
                            if dd is not None and dd <= T_LOAN and ((own is not None and own - dd >= T_LOAN_GAP) or (own is None and dd <= 0.1)):
                                ex = draw.get(c, [""])[0]
                                flags.append(dict(base, kind="loan", detail=f"{dn_name} {ex} ({dd:.2f}); target {own}", donor=dn_name,
                                                  score=round((own if own is not None else 1) - dd, 2)))
                    # D5 section votes: target vs lingua francas
                    cands = [("TARGET", own)] + [(n, mind(cls, donor_ref[n][0].get(c, []))) for n in LINGUA_FRANCAS
                                                 if not (tfam and donor_fam.get(n) == tfam)]
                    cands = [(n, x) for n, x in cands if x is not None]
                    if cands:
                        sec_votes[base["section"]][min(cands, key=lambda t: t[1])[0]] += 1
        lists_out.append(dict(list=vid, n_entries=len(rows), target=[ref.name.get(k) for k in sig], target_source=tsource,
                              target_family=tfam, affixes=affixes,
                              body_affix=dict(body_with=body_aff[(True, True)], body_without=body_aff[(True, False)],
                                              other_with=body_aff[(False, True)], other_without=body_aff[(False, False)]),
                              sections={s: dict(v) for s, v in sec_votes.items()}))
    # D6 circulating forms across families
    by = collections.defaultdict(list)
    for vid, fam, no, sf, g in all_forms:
        if len(no) >= 6:
            by[no].append((vid, fam, sf, g))
    for no, occ in by.items():
        fams = {fam for _, fam, _, _ in occ if fam}
        if len({v for v, *_ in occ}) >= 2 and len(fams) >= 2:
            for vid, fam, sf, g in occ:
                flags.append(dict(list=vid, tcp_id="", section="", gloss=g, form=sf, concepts="", extractor_note="",
                                  target_source="", kind="circulating",
                                  detail="also in: " + "; ".join(sorted({f"{v} ({fm})" for v, fm, _, _ in occ if v != vid})), score=float(len(fams))))
    df = pl.DataFrame(flags, infer_schema_length=None)
    df.write_parquet(f"{OUT}/flags.parquet")
    json.dump(lists_out, open(f"{OUT}/lists.json", "w"), ensure_ascii=False, indent=1)
    print(df.group_by("kind").len().sort("len", descending=True))


if __name__ == "__main__":
    main()
