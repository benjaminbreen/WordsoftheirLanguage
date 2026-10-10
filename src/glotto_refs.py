"""Glottolog references for a language: what linguists already cite.

Usage:  python src/glotto_refs.py <glottocode | language name> [more...]
        from glotto_refs import refs, find  (refs(glottocode) -> list of dicts; find(name) -> glottocodes)
Data: data/raw/glottolog_cldf/cldf (languages.csv, values.csv 'bib' parameter, sources.bib.zip).
"""
import csv
import functools
import re
import sys
import zipfile

B = "data/raw/glottolog_cldf/cldf/"


@functools.lru_cache(maxsize=1)
def _load():
    names = {}
    for r in csv.DictReader(open(B + "languages.csv", encoding="utf-8")):
        names[r["ID"]] = r["Name"]
    alt = {}
    try:
        for r in csv.DictReader(open(B + "names.csv", encoding="utf-8")):
            alt.setdefault(r["Name"].lower(), set()).add(r["Language_ID"])
    except FileNotFoundError:
        pass
    links = {}
    for r in csv.DictReader(open(B + "values.csv", encoding="utf-8")):
        if r["Parameter_ID"] == "bib":
            links[r["Language_ID"]] = [s for s in (r["Source"] or "").split(";") if s]
    z = zipfile.ZipFile(B + "sources.bib.zip")
    bib = z.read(z.namelist()[0]).decode("utf-8", "replace")
    entries = {}
    for m in re.finditer(r"@\w+\{([^,]+),(.*?)\n\}", bib, re.S):
        key, body = m.group(1), m.group(2)
        f = dict(re.findall(r"^\s{4}(\w+) = \{(.*)\},?$", body, re.M))
        entries[key] = dict(key=key, author=f.get("author", ""), year=f.get("year", ""),
                            title=re.sub(r"\s+", " ", f.get("title", "")))
    return names, alt, links, entries


def find(name):
    names, alt, _, _ = _load()
    n = name.lower()
    hits = {g for g, v in names.items() if v.lower() == n} | alt.get(n, set())
    if not hits:
        hits = {g for g, v in names.items() if n in v.lower()}
    return sorted(hits)


def refs(glottocode):
    names, _, links, entries = _load()
    return sorted((entries.get(k, dict(key=k, author="", year="", title="")) for k in links.get(glottocode, [])),
                  key=lambda e: e["year"])


if __name__ == "__main__":
    for q in sys.argv[1:]:
        gs = [q] if re.fullmatch(r"[a-z]{4}\d{4}", q) else find(q)
        for g in gs[:5]:
            rs = refs(g)
            print(f"== {g} {_load()[0].get(g)}: {len(rs)} refs")
            for e in rs:
                if e["year"] and e["year"][:4].isdigit() and int(e["year"][:4]) < 1900:
                    print(f"   {e['year']} {e['author'][:50]} — {e['title'][:90]}")
