"""Inter-annotator agreement between first-pass (annot/) and second-pass (annot2/) annotations."""
import glob, json, collections
import polars as pl

def load(pat):
    rows = [json.loads(l) for f in sorted(glob.glob(pat)) for l in open(f) if l.strip()]
    return pl.DataFrame(rows, infer_schema_length=None).with_columns(pl.col("n").cast(pl.Int64)).unique(["list", "n"], keep="last")

def kappa(a, b):
    n = len(a); cats = sorted(set(a) | set(b))
    po = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = collections.Counter(a), collections.Counter(b)
    pe = sum(ca[c] / n * cb[c] / n for c in cats)
    return (po - pe) / (1 - pe) if pe < 1 else 1.0, po

A = load("data/work/encounter/annot/*.jsonl"); B = load("data/work/encounter/annot2/*.jsonl")
J = A.join(B, on=["list", "n"], suffix="_2")
print("paired rows:", J.height)
coarse = lambda c: "ok" if c in ("ok", "phrase") else "artifact" if c != "uncertain" else "uncertain"
k, po = kappa(J["category"].to_list(), J["category_2"].to_list()); print(f"fine categories: agreement {po:.2f}, kappa {k:.2f}")
k2, po2 = kappa([coarse(c) for c in J["category"]], [coarse(c) for c in J["category_2"]]); print(f"artifact vs not: agreement {po2:.2f}, kappa {k2:.2f}")
for lst, g in J.group_by("list"):
    k3, p3 = kappa(g["category"].to_list(), g["category_2"].to_list()); print(f"  {lst[0]:14} n={g.height:3d} agree {p3:.2f} kappa {k3:.2f}")
both = J.filter((pl.col("category") == pl.col("category_2")) & ~pl.col("category").is_in(["ok", "phrase", "uncertain"]))
print("agreed artifacts:", both.height); print(both.group_by("category").len())
J.write_parquet("data/work/encounter/paired.parquet")
dis = J.filter(pl.col("category") != pl.col("category_2")).select("list", "n", "gloss", "form", "category", "evidence", "category_2", "evidence_2")
dis.write_csv("out/encounter_disagreements.csv")
