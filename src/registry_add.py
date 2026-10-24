"""Add or update tables in the registry (data/site/extra_tables.json) from transcription metadata.

Each spec gives the site-level choices (id, permanent WTL id, language, Glottolog code, region, short title);
everything else is read from data/work/extract3/<key>.meta.json written by the transcriber.
"""
import json
import os
import sys

REG = "data/site/extra_tables.json"


def first(m, *ks, default=""):
    for k in ks:
        v = m.get(k)
        if v not in (None, "", []):
            return v
    return default


def add(spec):
    key = spec["key"]
    m = json.load(open(f"data/work/extract3/{key}.meta.json", encoding="utf-8"))
    year = int(str(first(m, "year_printed", "year", default=spec.get("printed", 0)))[:4])
    jr = ", ".join(str(x) for x in (first(m, "journal"), first(m, "volume"), year,
                                   ("pp. " + str(m["pages"])) if m.get("pages") else "") if x)
    rec = dict(
        id=spec["id"], wtl=spec["wtl"], csv=f"data/work/extract3/{key}", ia=str(first(m, "ia")).rstrip("/").rsplit("/", 1)[-1],
        leaves=m.get("leaves") or [], lang=spec["lang"], glotto=spec["glotto"], region=spec["region"],
        heading=spec.get("heading") or first(m, "heading_as_printed", "heading_as_written"),
        short=spec["short"], author=spec.get("author") or first(m, "author", "author_as_printed"),
        collector=spec.get("collector") or first(m, "collector", "author"),
        place=spec.get("place") or first(m, "place"), heard=str(spec.get("heard") or first(m, "heard")),
        printed=year, title=spec.get("title") or first(m, "title_as_printed"),
        imprint=spec.get("imprint") or jr, about=spec.get("about") or first(m, "about"))
    for k in ("filt", "cols", "scan_note"):
        if k in spec:
            rec[k] = spec[k]
    reg = json.load(open(REG, encoding="utf-8")) if os.path.exists(REG) else []
    reg = [r for r in reg if r["id"] != rec["id"]] + [rec]
    reg.sort(key=lambda r: r["wtl"])
    json.dump(reg, open(REG, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return rec


if __name__ == "__main__":
    for s in json.load(open(sys.argv[1], encoding="utf-8")):
        r = add(s)
        print(r["wtl"], r["id"], r["printed"], r["lang"], "|", r["heading"][:60])
