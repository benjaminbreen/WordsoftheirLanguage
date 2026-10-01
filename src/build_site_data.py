"""Assemble out/site/data.json for the website: census, vocabularies with identifications, benchmark."""
import csv
import json
import os

import polars as pl

import identify2 as I

# id, csv path, profile, exclude (lineage), row filter, provenance notes (from the sources themselves)
LISTS = [
    ("rosier", "data/work/extract/rosier_A71306", "english", [], None,
     dict(collector="James Rosier", place="Penobscot Bay / St George's River, Maine", elicited="1605",
          printed="1625 (Purchas his Pilgrimes, pt. 4)", benchmark=True)),
    ("wood", "data/work/extract/wood_A15685", "english", [], None,
     dict(collector="William Wood", place="Massachusetts Bay", elicited="c. 1629-33", printed="1634", benchmark=True)),
    ("williams", "data/work/extract/williams_A66450", "english", ["narr1280"], None,
     dict(collector="Roger Williams", place="Narragansett Bay", elicited="1630s", printed="1643", benchmark=True)),
    ("smith_map", "data/work/extract/smith_map_A12466", "english", ["powh1243"], None,
     dict(collector="John Smith", place="Chesapeake, Virginia", elicited="1607-09", printed="1612", benchmark=True)),
    ("cartier", "data/work/extract/cartier_A18057", "french", ["laur1251"], None,
     dict(collector="Jacques Cartier (trans. John Florio)", place="Stadacona / Hochelaga, St Lawrence",
          elicited="1535-36", printed="1580 (English)", benchmark=True)),
    ("rochefort", "data/work/extract/rochefort_A57484", "english", ["isla1278", "asjp:CARIB_1665"], None,
     dict(collector="César de Rochefort (trans. John Davies)", place="Lesser Antilles", elicited="before 1658",
          printed="1666 (English)", benchmark=True)),
    ("scheffer", "data/work/extract/scheffer_A62332", "english", [], "lapland",
     dict(collector="Johannes Scheffer", place="Lapland", elicited="compiled 1673", printed="1674 (English)", benchmark=True)),
    ("knox", "data/work/extract/knox_A47586", "english", [], None,
     dict(collector="Robert Knox", place="Kandyan kingdom, Ceylon", elicited="1660-79", printed="1681", benchmark=True)),
    ("boothby", "data/work/extract/boothby_A28809", "english", [], None,
     dict(collector="Richard Boothby (from memory and a purser's papers)", place="Madagascar ('St. Laurence')",
          elicited="1630s-40s", printed="1646/47", benchmark=False)),
    ("vanneck", "data/work/extract/vanneck_A08052", "english", [], None,
     dict(collector="Second Dutch voyage (van Neck / Warwijck); English translator", place="Bantam, Java, Moluccas",
          elicited="1598-99", printed="1601 (English)", benchmark=True)),
    ("trinidad", "data/work/extract2/trinidad_A02495", "english", [], None,
     dict(collector="Robert Dudley's voyage (printed by Hakluyt)", place="Trinidad", elicited="1595",
          printed="1599-1600 (Hakluyt, Principal Navigations)", benchmark=False)),
    ("sami_burrough", "data/work/extract2/sami_burrough_A02495", "english", [], None,
     dict(collector="Stephen Burrough (printed by Hakluyt)", place="Kola coast (unlabelled in source)", elicited="1557",
          printed="1599 (Hakluyt)", benchmark=False)),
    ("pegu", "data/work/extract2/pegu_A21094", "english", [], None,
     dict(collector="First East India Company voyage (Lancaster)", place="'Pegu' (collected in the Indies)",
          elicited="1601-02", printed="1603", benchmark=False)),
    ("greenland", "data/work/extract2/greenland_olearius_A53322", "english", [], None,
     dict(collector="Adam Olearius (trans. John Davies)", place="Greenlanders brought to Denmark",
          elicited="1654-56", printed="1669 (English)", benchmark=False)),
    ("gthomas", "data/work/extract2/gthomas_A64548", "english", ["unam1242", "muns1251", "pidg1246"], None,
     dict(collector="Gabriel Thomas", place="Pennsylvania / West New Jersey", elicited="1680s-90s",
          printed="1698", benchmark=False)),
    ("chilesian", "data/work/extract2/chilesian_ogilby_A53222", "english", [], None,
     dict(collector="Elias Herckmans (via John Ogilby)", place="Valdivia, Chile", elicited="1643",
          printed="1671 (Ogilby, America)", benchmark=False)),
    ("tupi_ogilby", "data/work/extract2/tupi_ogilby_A53222", "english", [], None,
     dict(collector="via John Ogilby (Dutch Brazil sources)", place="Brazil", elicited="17th c.",
          printed="1671 (Ogilby, America)", benchmark=False)),
    ("ludolf_gallan", "data/work/extract2/ludolf_gallan_A49450", "english", [], "gallan",
     dict(collector="Hiob Ludolf (informant Abba Gregorius)", place="Ethiopia", elicited="1650s",
          printed="1682 (English)", benchmark=False)),
]


def read_rows(path, filt):
    rows = list(csv.DictReader(open(path + ".entries.csv", encoding="utf-8")))
    if filt:
        rows = [r for r in rows if filt in (r.get("form_language_label_as_printed") or "").lower()]
    return rows


def main():
    os.makedirs("out/site", exist_ok=True)
    meta = pl.read_parquet("data/work/meta.parquet")
    md = {r["tcp_id"]: r for r in meta.iter_rows(named=True)}
    ref = I.Reference()
    cm = I.ConceptMapper()
    vocabs = []
    for vid, path, prof, excl, filt, prov in LISTS:
        rows = read_rows(path, filt)
        tcp = path.rsplit("_", 1)[-1]
        ents = [(r["gloss_as_printed"], r["form_as_printed"]) for r in rows
                if r.get("gloss_as_printed") and r.get("form_as_printed")]
        res = I.identify(ents, ref, set(excl), prof)
        m = md.get(tcp, {})
        heads = []
        for r in rows:
            h = (r.get("section_heading") or "").strip()
            if h and h not in heads:
                heads.append(h)
        labels = sorted({r.get("form_language_label_as_printed") for r in rows if r.get("form_language_label_as_printed")})
        vocabs.append(dict(
            id=vid, tcp_id=tcp, title=m.get("title"), author=m.get("author"), year=m.get("year"),
            provenance=prov, excluded=excl, headings=heads[:6], labels=labels,
            entries=[dict(n=i + 1, gloss=r["gloss_as_printed"], form=r["form_as_printed"],
                          concepts=sorted(cm(r["gloss_as_printed"])), note=r.get("note") or "")
                     for i, r in enumerate(rows)],
            ident=dict(status=res["status"], hierarchy=res["hierarchy"], n_concepts=res["n_concepts"],
                       affixes=res["affixes_removed"], leading=res["leading"],
                       candidates=[{k: v for k, v in t.items()} for t in res["candidates"][:12]])))
        print(vid, res["status"], res["hierarchy"][-2:] if res["hierarchy"] else res["leading"])
    census = pl.read_parquet("data/work/census_v0.parquet")
    cen = []
    for r in census.iter_rows(named=True):
        cen.append({k: (list(v) if isinstance(v, (list, tuple)) else v) for k, v in r.items()})
    bench = json.load(open("out/benchmark.json"))
    json.dump(dict(census=cen, vocabularies=vocabs, benchmark=bench), open("out/site/data.json", "w"),
              ensure_ascii=False, default=str)
    print("wrote out/site/data.json", os.path.getsize("out/site/data.json") // 1024, "KB")


if __name__ == "__main__":
    main()
