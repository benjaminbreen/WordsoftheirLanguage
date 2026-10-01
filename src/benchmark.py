"""Leave-lineage-out benchmark for historical-wordlist identification, with null calibration.

For each benchmark list: exclude reference doculects descended from the same source
lineage, mask everything but (gloss, form), run identify2, and score family/subgroup hits
against the expected Glottolog node. Null calibration: the same lists with forms shuffled
across glosses, run through the identical pipeline, give the distribution of the best z
that pure noise achieves in a search over ~16k doculects.
"""
import json
import random
import sys

import numpy as np

import identify2 as I

CASES = [
    # name, profile, exclude (glottocodes or doculect keys), expected family, expected subgroup node
    ("rosier_A71306", "english", [], "Algic", "Northern Eastern Algonquian"),
    ("wood_A15685", "english", [], "Algic", "Southern New England Algonquian"),
    ("williams_A66450", "english", ["narr1280"], "Algic", "Southern New England Algonquian"),
    ("smith_map_A12466", "english", ["powh1243"], "Algic", "Eastern Algonquian"),
    ("cartier_A18057", "french", ["laur1251"], "Iroquoian", "Northern Iroquoian"),
    ("rochefort_A57484", "english", ["isla1278", "asjp:CARIB_1665"], "Arawakan", "Island Carib-Garifuna"),
    ("scheffer_A62332", "english", [], "Uralic", "Saami"),
    ("knox_A47586", "english", [], "Indo-European", "Sinhalaic"),
    ("boothby_A28809", "english", [], None, None),     # exploratory: disputed
    ("vanneck_A08052", "english", [], "Austronesian", "Malayic"),
]


def entries_for(name):
    ents = I.read_entries(f"data/work/extract/{name}.entries.csv")
    if name.startswith("scheffer"):
        import csv
        rows = list(csv.DictReader(open(f"data/work/extract/{name}.entries.csv", encoding="utf-8")))
        ents = [(r["gloss_as_printed"], r["form_as_printed"]) for r in rows
                if "lapland" in (r["form_language_label_as_printed"] or "").lower()]
    return ents


def node_hit(res, node, depth_ok=True):
    if node is None:
        return None
    hier = [n for n, s in res["hierarchy"]]
    return node in hier


def top_family(res):
    c = res["candidates"]
    return c[0]["path"][0] if c else None


def run(vowels, n_null=10, seed=1):
    I.VOWELS = vowels
    ref = I.Reference()
    rows, null_z = [], []
    rng = random.Random(seed)
    for name, prof, excl, fam, sub in CASES:
        ents = entries_for(name)
        res = I.identify(ents, ref, set(excl), prof)
        best = res["candidates"][0] if res["candidates"] else None
        # null: shuffle forms across glosses
        nz = []
        for k in range(n_null):
            forms = [f for _, f in ents]
            rng.shuffle(forms)
            nres = I.identify([(g, f) for (g, _), f in zip(ents, forms)], ref, set(excl), prof, seed=k)
            if nres["candidates"]:
                nz.append(max(t["z"] for t in nres["candidates"]))
        null_z += nz
        rows.append(dict(
            name=name, concepts=res["n_concepts"], status=res["status"],
            top=best and best["name"], top_family=best and best["path"][0], top_z=best and best["z"],
            max_z=max((t["z"] for t in res["candidates"]), default=None),
            fam_expected=fam, fam_top1=(best and fam and best["path"][0] == fam),
            fam_in_hier=node_hit(res, fam), sub_in_hier=node_hit(res, sub),
            hierarchy=res["hierarchy"], null_max_z=nz))
    return rows, null_z


if __name__ == "__main__":
    out = {}
    for vowels in (True,):
        rows, null_z = run(vowels)
        thr = float(np.percentile(null_z, 99)) if null_z else None
        out[f"vowels={vowels}"] = dict(rows=rows, null_z=null_z, null_z_95=thr)
        print(f"\n=== vowels={vowels}  null max-z 95th pct = {thr:.2f}  (n={len(null_z)}, max={max(null_z):.2f})")
        for r in rows:
            passed = r["max_z"] is not None and r["max_z"] > thr
            print(f"{r['name']:18} c={r['concepts']:3d} top={str(r['top'])[:24]:24} {str(r['top_family'])[:14]:14} "
                  f"maxz={r['max_z'] or 0:5.2f} {'PASS' if passed else 'abst'} fam1={r['fam_top1']} "
                  f"sub={r['sub_in_hier']} | {' > '.join(n for n, s in r['hierarchy'][-3:])}")
    json.dump(out, open("out/benchmark.json", "w"), indent=1, default=str)
