"""Compare computational detector flags with protocol annotations; per-list artifact rates.

Annotations (data/work/encounter/annot/*.jsonl) are the silver standard here; a human-checked sample
of them is still needed before publication.
"""
import collections
import csv
import glob
import json

import polars as pl

from build_site_data import LISTS

KIND_TO_CAT = {"loan": "loan", "neighbour_concept": "ostension", "interactional_as_lexeme": "interactional",
               "phrase": "phrase"}


def row_index(path):
    """(gloss, form) -> 1-based row numbers in the CSV."""
    idx = collections.defaultdict(list)
    for i, r in enumerate(csv.DictReader(open(path + ".entries.csv", encoding="utf-8")), 1):
        idx[(r["gloss_as_printed"], r["form_as_printed"])].append(i)
    return idx


def main():
    ann = [json.loads(l) for f in sorted(glob.glob("data/work/encounter/annot/*.jsonl")) for l in open(f) if l.strip()]
    A = pl.DataFrame(ann, infer_schema_length=None).with_columns(pl.col("n").cast(pl.Int64))
    A = A.unique(["list", "n"], keep="last")
    flags = pl.read_parquet("data/work/encounter/flags.parquet")
    paths = {vid: path for vid, path, *_ in LISTS}
    frows = []
    for r in flags.iter_rows(named=True):
        if r["kind"] not in KIND_TO_CAT or r["list"] not in paths:
            continue
        for n in row_index(paths[r["list"]]).get((r["gloss"], r["form"]), []):
            frows.append(dict(list=r["list"], n=n, kind=r["kind"], cat=KIND_TO_CAT[r["kind"]]))
    F = pl.DataFrame(frows).unique(["list", "n", "cat"])
    print("annotated rows:", A.height)
    print(A.group_by("category").len().sort("len", descending=True))
    # precision / recall per detector against annotation category (conf >= 0.6 counts as positive)
    pos = A.filter(pl.col("confidence") >= 0.6)
    out = {}
    for cat in ["loan", "ostension", "interactional", "phrase"]:
        det = set(map(tuple, F.filter(pl.col("cat") == cat).select("list", "n").rows()))
        gold = set(map(tuple, pos.filter(pl.col("category") == cat).select("list", "n").rows()))
        annotated = set(map(tuple, A.select("list", "n").rows()))
        det &= annotated
        tp = len(det & gold)
        out[cat] = dict(flagged=len(det), annotated_pos=len(gold), tp=tp,
                        precision=round(tp / len(det), 2) if det else None,
                        recall=round(tp / len(gold), 2) if gold else None)
    print(json.dumps(out, indent=1))
    rates = (A.group_by("list").agg(pl.len().alias("n"),
             *[(pl.col("category") == c).sum().alias(c) for c in
               ["loan", "ostension", "interactional", "inflected", "phrase", "wrong_language", "print_error", "uncertain"]])
             .sort("list"))
    pl.Config.set_tbl_cols(20); pl.Config.set_tbl_width_chars(200)
    print(rates)
    rates.write_csv("out/encounter_rates_pilot.csv")
    json.dump(out, open("out/encounter_detector_eval.json", "w"), indent=1)


if __name__ == "__main__":
    main()
